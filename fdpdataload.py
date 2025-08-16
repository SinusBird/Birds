import os
import io
from ftplib import FTP_TLS
from io import BytesIO
import pandas as pd


def get_ftp_data():
    ftp_user = os.getenv("BIRD_FTP_USER")
    ftp_pw = os.getenv("BIRD_FTP_PW")
    ftp_host = os.getenv("BIRD_FTP_SERVER")
    ftp_dir = "/public_html/bird-analytics/" ## funktioniert nicht

    ftp = FTP_TLS(ftp_host)
    ftp.login(ftp_user,ftp_pw)
    ftp.prot_p()  # activate encripted date transfer

    file_list = ftp.nlst() # lists of all files in the current ftp directory

    print("Aktuelles Verzeichnis:", ftp.pwd())
    print("Inhalt:", file_list)

    xlsx_files = [f for f in file_list if f.lower().endswith(".xlsx")]

    dataframes = {}

    for filename in xlsx_files:
        if filename.endswith(".xlsx"):
            with io.BytesIO() as buffer:
                ftp.retrbinary(f"RETR {filename}", buffer.write)
                buffer.seek(0)
                df = pd.read_excel(buffer)
                key_name = filename.rsplit(".", 1)[0]
                dataframes[key_name] = df

    ftp_files = list(dataframes.keys())

    expected_files = {
        "TLKPCATCHINGLURES": None,
        "TLKPAGE": None,
        "TLKPSEX": None,
        "tblRefer": None,
        "TLKPACCURACYDATE": None,
        "TLKPACCURACYPLACE": None,
        "TLKPSPECIES": None,
        "TLKPVERIFICATIONRING": None,
        "TLKPSTATUSBROODSIZE": None,
        "TLKPCATCHINGMETHODS": None,
        "TLKPRELATION": None,
        "TLKPRECOVERYCHANCES": None,
        "tblGeoTab": None,
        "TLKPRINGINGSCHEME": None,
        "tblRinging": None,
        "TLKPCHANGESTORING": None,
        "TLKPPLACECODE": None,
        "TLKPFINDDETAILS": None,
        "TLKPFINDCIRCUMSTANCES": None,
        "tblOpen": None,
        "TLKPFINDCONDITIONS": None
    }

    # Überprüfe, ob erwartete Dateien schon geladen sind
    for key in expected_files:
        if key in dataframes:
            expected_files[key] = dataframes[key]
            #print(f"✅ '{key}' erfolgreich geladen.")
        else:
            print(f"⚠️ '{key}' nicht gefunden.")

    ftp.quit()  # Verbindung erst hier schließen

    # Beispielausgabe
    #for name, df in expected_files.items():
    #    if df is not None:
    #        print(f"--- DataFrame: {name} ---")
    #        print(df.head(3))
    #        print("\n")
    #    else:
    #        print(f"--- DataFrame: {name} ist nicht geladen ---\n")

    # Zugriff auf die geladenen DataFrames

    ### fact values
    fact_dfs = {
        "df_ringing": expected_files["tblRinging"]
    }

    ###dim values
    dim_dfs = {
        "df_place_code": expected_files["TLKPPLACECODE"],
        "df_lures": expected_files["TLKPCATCHINGLURES"],
        "df_age": expected_files["TLKPAGE"],
        "df_sex": expected_files["TLKPSEX"],
        "df_refer": expected_files["tblRefer"], # wofür?
        "df_accuracy_date": expected_files["TLKPACCURACYDATE"],
        "df_accuracy_place": expected_files["TLKPACCURACYPLACE"],
        "df_species": expected_files["TLKPSPECIES"],
        "df_verification_ring": expected_files["TLKPVERIFICATIONRING"],
        "df_status_broodsize": expected_files["TLKPSTATUSBROODSIZE"],
        "df_catching_methods": expected_files["TLKPCATCHINGMETHODS"],
        "df_bird_relation": expected_files["TLKPRELATION"],
        "df_recovery_chances": expected_files["TLKPRECOVERYCHANCES"],
        "df_ringing_scheme": expected_files["TLKPRINGINGSCHEME"],
        "df_changes_to_ring": expected_files["TLKPCHANGESTORING"],
        "df_details": expected_files["TLKPFINDDETAILS"],
        "df_circumstances": expected_files["TLKPFINDCIRCUMSTANCES"],
        "df_conditions": expected_files["TLKPFINDCONDITIONS"],
        "df_open": expected_files["tblOpen"],
        "df_geo_tab": expected_files["tblGeoTab"]
    }

    return fact_dfs, dim_dfs




