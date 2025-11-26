import pandas as pd
from helpers import TemporalSplitter

def main():
    df = pd.read_csv("C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\nba_train_data.csv")

    splitter = TemporalSplitter(date_col="GAME_DATE")

    train_df, val_df, test_df = splitter.split(df)

    # Save
    train_df.to_csv("train.csv", index=False)
    val_df.to_csv("val.csv", index=False)
    test_df.to_csv("test.csv", index=False)

    # Print summary
    summary = splitter.summary(df, train_df, val_df, test_df)
    print(summary)

if __name__ == "__main__":
    main()
