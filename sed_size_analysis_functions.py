# sed_size_analysis_functions.py
"""Modules for sediment size analysis data processing"""

import pandas as pd
import numpy as np


class hydrometer_calcs:
    """
    Takes hydrometer data and returns percent sand, silt, and clay.
    """

    def __init__(self, path_to_data, path_to_config, path_to_colnames, path_to_calcset):

        self.path_to_data = path_to_data
        self.path_to_config = path_to_config
        self.path_to_colnames = path_to_colnames
        self.path_to_calcset = path_to_calcset

        # Load data
        self.data = pd.read_csv(self.path_to_data)
        self.config = pd.read_csv(self.path_to_config)
        self.colnames = pd.read_csv(self.path_to_colnames)
        self.calcset = pd.read_csv(self.path_to_calcset)

        # Validate inputs
        self._validate_columns()
        self._validate_parameters()

        # Output dataframe (safe copy)
        self.results = self.data.copy()

        # Build parameter dictionary
        self.params = (
            self.config
            .set_index("Parameter")["Value"]
            .to_dict()
        )

        # Build calculation settings dictionary
        self.calcset = (
            self.calcset
            .set_index("Setting")["Value"]
            .to_dict()
        )

        print("hydrometer_calcs initialized")

    # -----------------------------
    # Helpers
    # -----------------------------
    def _validate_columns(self):
        expected_cols = self.colnames.loc[:, "col_name_in_data"].dropna().tolist()
        missing = set(expected_cols) - set(self.data.columns)

        if missing:
            raise ValueError(f"Missing columns: {missing}")

    def _validate_parameters(self):
        required = {"mu", "rho_l", "rho_s", "g", "L0", "k"}
        available = set(self.config["Parameter"])

        missing = required - available
        if missing:
            raise ValueError(f"Missing parameters: {missing}")
        
        
    def _col(self, name):
        """
        Return the data column corresponding to a standardized name.

        Parameters
        ----------
        name : str
            Standardized column name used in code

        Returns
        -------
        pandas.Series
        """

        try:
            raw_name = self.colnames.loc[
                self.colnames["Variable"] == name, "col_name_in_data"
            ].iloc[0]
        except IndexError:
            raise KeyError(f"'{name}' not found in colnames variable column")

        if raw_name not in self.data.columns:
            raise KeyError(
                f"Column '{raw_name}' (mapped from '{name}') not found in data"
            )

        return self.data[raw_name]
    
    def interpolate_P(self, row, target):
        X_vals = row[self.X_cols].values
        P_vals = row[self.P_cols].values

        sorted_idx = np.argsort(X_vals)
        X_vals = X_vals[sorted_idx]
        P_vals = P_vals[sorted_idx]

        warning = ""
        for i in range(len(X_vals) - 1):
            if X_vals[i] <= target <= X_vals[i+1]:
                X0, X1 = X_vals[i], X_vals[i+1]
                P0, P1 = P_vals[i], P_vals[i+1]
                col_X0 = self.X_cols[sorted_idx[i]].split("_")[1]
                col_X1 = self.X_cols[sorted_idx[i+1]].split("_")[1]
                warning = f"Used data from times {col_X0} and {col_X1} to interpolate {target*10000}um"

                if X1 == X0:
                    return P0, warning
                return P0 + (P1 - P0) * (np.log(target) - np.log(X0)) / (np.log(X1) - np.log(X0)), warning

        if  self.calcset["extrapolation_handling"] == "truncate":

            if target <= X_vals[0]:
                warning = f"{target*10000}um is smaller than all X values; used P for smallest X"
                return P_vals[0], warning

            if target >= X_vals[-1]:
                warning = f"{target*10000}um is larger than all X values; used P for largest X"
                return P_vals[-1], warning
            
        if  self.calcset["extrapolation_handling"] == "extrapolate":

            if target <= X_vals[0]:
                X0, X1 = X_vals[0], X_vals[1]
                P0, P1 = P_vals[0], P_vals[1]
                col_X0 = self.X_cols[sorted_idx[i]].split("_")[1]
                col_X1 = self.X_cols[sorted_idx[i+1]].split("_")[1]
                warning = f"{target*10000}um is smaller than all X values; Used data from times {col_X0} and {col_X1} to interpolate {target*10000}um"

                return P0 + (P1 - P0) * (np.log(target) - np.log(X0)) / (np.log(X1) - np.log(X0)), warning

            if target >= X_vals[-1]:
                X0, X1 = X_vals[-2], X_vals[-1]
                P0, P1 = P_vals[-2], P_vals[-1]
                col_X0 = self.X_cols[sorted_idx[i]].split("_")[1]
                col_X1 = self.X_cols[sorted_idx[i+1]].split("_")[1]
                warning = f"{target*10000}um is smaller than all X values; Used data from times {col_X0} and {col_X1} to interpolate {target*10000}um"
                return P0 + (P1 - P0) * (np.log(target) - np.log(X0)) / (np.log(X1) - np.log(X0)), warning
            

        return np.nan, "Interpolation failed"

    # -----------------------------
    # Main calculation
    # -----------------------------
    def calc_percent_size(self):

        # Physical constants
        mu = float(self.params["mu"])
        rho_l = float(self.params["rho_l"])
        rho_s = float(self.params["rho_s"])
        g = float(self.params["g"])
        L0 = float(self.params["L0"])
        k = float(self.params["k"])

        times = ["30", "60", "5400", "86400"]

        # Prep lists for interpolation
        self.X_cols = [f"X_{t}" for t in times]
        self.P_cols = [f"P_{t}" for t in times]
        
        print(self.X_cols)


        # 1. Temperature correction of hydrometer reading
        for t in times:
            self.results[f"temp_corr_{t}"] = (0.36 * (self._col(f"T{t}_temp") - 20))

        # 2. Corrected hydrometer readings
        for t in times:
            self.results[f"R{t}_corr"] = (self._col(f"R_{t}") + self.results[f"temp_corr_{t}"] - self._col(f"R_b_{t}"))

        # 3. Effective depth
        for t in times:
            self.results[f"hprime_{t}"] = (L0 - k * self._col(f"R_{t}")) #note, this uses the non-corrected r value (as done by Gee & Bauder)

        # 4. Equivalent particle diameter X (cm)
        # Note: times in seconds
        for t in times:
            self.results[f"X_{t}"] = ((18 * mu *  self.results[f"hprime_{t}"]) / (g * (rho_s - rho_l) * float(t)))**0.5

        # 5. Percent finer at each time
        for t in times:
            self.results[f"P_{t}"] = self.results[f"R{t}_corr"] / self._col(f"C") * 100 #note this uses the corrected r value (as done by Gee & Bauder)

        # 6. Interpolate P2um (0.0002cm)
        self.results[["P_2um", "Warning_2um"]] = self.results.apply(lambda row: pd.Series(self.interpolate_P(row, target=0.0002)), axis=1)

        # 7. Interpolate P50um (0.0050cm)
        self.results[["P_50um", "Warning_50um"]] = self.results.apply(lambda row: pd.Series(self.interpolate_P(row, target=0.0050)), axis=1)


        # 8. Calculate size fractions
        self.results["P_clay"] = self.results["P_2um"]
        self.results["P_sand"] = 100 - self.results["P_50um"]
        self.results["P_silt"] = 100 - (self.results["P_sand"] + self.results["P_clay"])

        return self.results


if __name__ == "__main__":

    hc = hydrometer_calcs(path_to_data="C:/Users/josie/Downloads/sed_size_analysis_example/sedsizedata_sample_taylor.csv", 
                          path_to_config= "C:/Users/josie/Downloads/sed_size_analysis_example/config_files/config.csv", 
                          path_to_colnames= "C:/Users/josie/Downloads/sed_size_analysis_example/config_files/colnames.csv", 
                          path_to_calcset="C:/Users/josie/Downloads/sed_size_analysis_example/config_files/calcset.csv")

    results = hc.calc_percent_size()
    
    print(results)

    # Save output
    results.to_csv("C:/Users/josie/Downloads/sed_size_analysis_example/output.csv", index=False)
