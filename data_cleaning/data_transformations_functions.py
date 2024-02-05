import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


def create_bar_graph(data, options: dict):
    # Set the font to Microsoft Sans Serif
    matplotlib.rcParams["font.family"] = options["font_family"]
    matplotlib.rcParams["font.sans-serif"] = options["font"]
    dataframe = data.copy()

    if options["format_long_names"] == True:
        # Insert newline characters to break long labels
        dataframe.loc[:, "name"] = dataframe["name"].apply(
            lambda name: name.replace(" ", "\n")
        )

    # Create a horizontal bar chart using Seaborn with a color-coded hue
    plt.figure(figsize=(12, 6), dpi=200)  # Adjust the figure size as needed
    ax = sns.barplot(
        data=dataframe,
        x=options["x"],
        y=options["y"],
        palette=options["palette"],
        edgecolor="black",
    )
    plt.xlabel(options["xlabel"], fontweight="bold")
    plt.ylabel(options["ylabel"])

    # Set the title to bold
    plt.title(options["title"], fontsize=20, fontweight="bold")

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Add mean values next to the bars
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_width())}",
            (p.get_width(), p.get_y() + p.get_height() / 2.0),
            ha="center",
            va="center",
            fontsize=11,
            color="black",
            fontweight="bold",
            xytext=(25, 0),
            textcoords="offset points",
        )

    # Remove x-axis labels and ticks on the bottom
    ax.set_xticks([])
    ax.set_xticklabels([])
    plt.axvline(x=0, color="black", linewidth=2)

    # Display the chart
    plt.tight_layout()  # Ensures labels are not cut off
    plt.show()


def preprocess_streamers_data(streamers):
    """
    Filters dataframe by date after '2023-07-23 23:59:59', transforms STREAMER_VIEWS column to numeric and drops the extra view column
    """
    filter_date = pd.Timestamp("2023-07-23 23:59:59")
    streamers["DATE"] = pd.to_datetime(streamers["DATE"])
    streamers = streamers[streamers["DATE"] > filter_date]
    streamers_preprocessed = streamers.copy()
    streamers_preprocessed["VIEWS"] = (
        streamers_preprocessed["STREAMER_VIEWS"].copy().apply(transform_to_numeric)
    )
    streamers_preprocessed.drop(columns=["STREAMER_VIEWS"], inplace=True)
    return streamers_preprocessed


def filter_popular_streamers(streamers):
    """
    Filters streamers dataframe by streamers that appear more than 15 times
    """
    streamers_count = streamers["STREAMER_NAMES"].value_counts()
    popular_streamers = streamers[
        streamers["STREAMER_NAMES"].isin(streamers_count[streamers_count > 15].index)
    ]
    return popular_streamers


def calculate_mean_viewers(popular_streamers):
    """
    Calculates the mean views for each streamer
    """
    return (
        popular_streamers.groupby("STREAMER_NAMES")["VIEWS"]
        .mean()
        .reset_index()
        .sort_values(by="VIEWS", ascending=False)
    )


def calculate_live_time(popular_streamers):
    """
    Calculates the average live time for each streamer
    """
    grouped_streamers = popular_streamers.sort_values(by=["STREAMER_NAMES", "DATE"])
    grouped_streamers["TIME_DIFF"] = (
        grouped_streamers.groupby("STREAMER_NAMES")["DATE"].diff().dt.total_seconds()
    )
    filtered_streamers = grouped_streamers[
        (grouped_streamers["TIME_DIFF"] > 2000)
        | (grouped_streamers["TIME_DIFF"].isna())
    ]
    live_time = (
        grouped_streamers[~grouped_streamers.index.isin(filtered_streamers.index)][
            "TIME_DIFF"
        ].mean()
        / 60
    )
    live_time_df = popular_streamers["STREAMER_NAMES"].value_counts().reset_index()
    live_time_df.columns = ["STREAMER_NAMES", "LIVE_TIME"]
    live_time_df["LIVE_TIME"] = live_time_df["LIVE_TIME"] * live_time
    return live_time_df


def get_most_frequent_category_and_lang(popular_streamers):
    """
    Gets the most frequent category and language for each streamer
    """
    most_frequent_category = popular_streamers.groupby("STREAMER_NAMES")[
        "CATEGORY_NAMES"
    ].agg(lambda x: x.mode().iloc[0])
    most_frequent_lang = (
        popular_streamers.groupby("STREAMER_NAMES")["LANG"]
        .agg(lambda x: x.mode().iloc[0])
        .reset_index()
    )
    result_df = most_frequent_category.reset_index()
    result_df.columns = ["STREAMER_NAMES", "MOST_FREQUENT_CATEGORY"]
    most_frequent_categories = result_df.reset_index()
    return most_frequent_categories, most_frequent_lang


def merge_and_finalize_dataframes(
    mean_viewers, most_frequent_categories, most_frequent_lang, live_time_df
):
    """
    Merges all the dataframes into a single one
    """
    merged_data = mean_viewers.merge(most_frequent_categories, on="STREAMER_NAMES")
    merged_data = merged_data.merge(most_frequent_lang, on="STREAMER_NAMES")
    merged_data = merged_data.merge(live_time_df, on="STREAMER_NAMES")
    merged_data.drop(columns="index", inplace=True)
    return merged_data


def translate_lang_names_to_english(streamers_df, dict_lang_names_in_english):
    """
    Translates the language names to english
    """
    streamers_df["LANG"] = streamers_df["LANG"].apply(
        lambda lang: dict_lang_names_in_english[lang]
    )
    return streamers_df


def add_gender_column(streamers_df):
    """
    Add gender column to the dataframe
    """
    with open(
        "data_cleaning/gender_prediction/output/female_streamers.txt",
        "r",
        encoding="UTF-8",
    ) as p:
        female_list = [name.strip() for name in p.readlines()]

    def get_gender(name):
        return "Female" if name in female_list else "Male"

    streamers_df["SEX"] = streamers_df["STREAMER_NAMES"].apply(get_gender)
    return streamers_df


def create_column_graph(data, options: dict):
    # Set the font to Microsoft Sans Serif
    matplotlib.rcParams["font.family"] = options["font_family"]
    matplotlib.rcParams["font.sans-serif"] = options["font"]
    dataframe = data.copy()

    # Insert newline characters to break long labels
    dataframe.loc[:, "name"] = dataframe["name"].apply(
        lambda name: name.replace(" ", "\n")
    )

    # Create a bar chart using Seaborn with a color-coded hue
    plt.figure(figsize=(12, 6), dpi=200)  # Adjust the figure size as needed
    ax = sns.barplot(
        data=dataframe,
        x="name",
        y="mean_views",
        palette=options["palette"],
        edgecolor="black",
    )
    plt.xlabel(options["xlabel"], fontweight="bold")
    plt.ylabel(options["ylabel"])

    # Set the title to bold
    # plt.title('Top 10 games by mean views over the week', fontsize=20, fontweight='bold')
    plt.title(options["title"], fontsize=20, fontweight="bold")

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Add mean values above the bars
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height())}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            fontsize=11,
            color="black",
            fontweight="bold",
            xytext=(0, 10),
            textcoords="offset points",
        )

    # Remove y-axis labels and ticks on the left
    ax.set_yticks([])
    ax.set_yticklabels([])
    plt.axhline(y=0, color="black", linewidth=2)

    # Display the chart
    plt.tight_layout()  # Ensures labels are not cut off
    plt.show()


def create_annotation_text(ax):
    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Add mean values next to the bars
    for p in ax.patches:
        u = p.get_width()
        if pd.notna(u):
            ax.annotate(
                f"{int(p.get_width())}",
                (p.get_width(), p.get_y() + p.get_height() / 2.0),
                ha="center",
                va="center",
                fontsize=11,
                color="black",
                fontweight="bold",
                xytext=(25, 0),
                textcoords="offset points",
            )
    return ax


# creates pipeline to convert views column to integer
def transform_to_numeric(value):
    if "K" in value:
        return int(float(value.replace("K", "").split()[0]) * 1000)
    elif "M" in value:
        return int(float(value.replace("M", "").split()[0]) * 1000000)
    else:
        return int(value.split()[0])


def create_bar_graph2(data, x_label, y_label, options):
    # Set the font to Microsoft Sans Serif
    matplotlib.rcParams["font.family"] = options["font_family"]
    matplotlib.rcParams["font.sans-serif"] = options["font"]
    dataframe = data.copy()

    x_label = x_label
    y_label = y_label

    # Insert newline characters to break long labels
    """dataframe.loc[:, "name"] = dataframe["name"].apply(
        lambda name: name.replace(" ", "\n")
    )"""

    # Create a horizontal bar chart using Seaborn with a color-coded hue
    plt.figure(figsize=(12, 6), dpi=200)  # Adjust the figure size as needed
    ax = sns.barplot(
        data=dataframe,
        x=x_label,
        y=y_label,
        palette=options["palette"],
        edgecolor="black",
        hue=options["hue"],
        dodge=options["dodge"],
    )
    plt.xlabel(options["xlabel"], fontweight="bold")
    plt.ylabel(options["ylabel"])

    # Set the title to bold
    plt.title(options["title"], fontsize=20, fontweight="bold")

    # Remove top and right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Add mean values next to the bars
    for p in ax.patches:
        u = p.get_width()
        if pd.notna(u):
            ax.annotate(
                f"{int(p.get_width())}",
                (p.get_width(), p.get_y() + p.get_height() / 2.0),
                ha="center",
                va="center",
                fontsize=11,
                color="black",
                fontweight="bold",
                xytext=(25, 0),
                textcoords="offset points",
            )
    legend = ax.legend(title="Custom Legend Title")
    legend.get_title().set_fontsize(12)

    # Remove x-axis labels and ticks on the bottom
    ax.set_xticks([])
    ax.set_xticklabels([])
    plt.axvline(x=0, color="black", linewidth=2)

    # Display the chart
    plt.tight_layout()  # Ensures labels are not cut off
    plt.show()


if __name__ == "__main__":
    print("This is a module and cannot be run as a script")
