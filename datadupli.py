
import pandas as pd
import numpy as np

# Function to randomly duplicate rows and increment BirdID (based on current distribution)
def random_duplicate_and_increment_birdid(df, max_duplicates=20, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Optional: Set seed for reproducibility

    # Generate a random number of duplicates for each row, based on the distribution of current data
    repeat_counts = np.random.randint(1, max_duplicates + 1, size=len(df))
    
    # Repeat rows based on the random counts
    duplicated_df = df.loc[df.index.repeat(repeat_counts)].reset_index(drop=True)
    
    # Update BirdID with a continuous sequence
    duplicated_df['BirdID'] = np.arange(1, len(duplicated_df) + 1)
    
    return duplicated_df, repeat_counts


# Generate additional random dates to spread out catches more evenly over the year
def generate_additional_dates(df, period_start, period_end, n_extra=2000, seed=None):
    if seed is not None:
        np.random.seed(seed)
    
    # Create random additional date range from the original data
    date_range = pd.date_range(start=period_start, end=period_end, freq='D')
    extra_dates = np.random.choice(date_range, size=n_extra, replace=True)
    
    # Create new data entries with random dates
    additional_data = df.sample(n=n_extra, replace=True).copy()
    additional_data['DateTimeID'] = extra_dates
    additional_data['BirdID'] = np.arange(len(df)+1, len(df)+n_extra+1)  # New unique BirdIDs
    return pd.concat([df, additional_data], ignore_index=True)
