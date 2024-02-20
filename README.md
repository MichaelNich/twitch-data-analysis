# <h1>twitch-data-analysis</h1>
## **A Week in the Life of Twitch: Analyzing Streamer, Game, and Viewer Dynamics**

[LIVE PROJECT LINK](https://michaelnich.github.io/portfolio/projects/project1/project1.html#Outline)


### *This data analysis project explores Twitch streaming trends, focusing on streamers, games, and viewer behavior. The dataset was collected from Twitch.tv during a one-week period, capturing streamers broadcasting in various languages. The methodology involves web scraping, data transformation, data visualization and storage in an IBM Db2 database.*

## Disclaimer:
### Data Collection:
Data was collected from Twitch.tv between July 24, 2024, 00:00 (UTC-5), and July 30, 2024, 23:59 (UTC-5)
The dataset includes streamers broadcasting in the following languages: Spanish, Chinese, Portuguese, English, French, Italian, Korean, Japanese, Polish, German, Turkish, Russian, and Ukrainian.
Data was gathered at 15-minute intervals to adhere to Twitch API guidelines and prevent rate-limiting errors.
### Limitations:
The dataset reflects a limited time frame and specific languages, potentially impactinggeneralizability of findings.
Data collection frequency (15 minutes) may not capture all streaming events or fluctuations.
Data accuracy relies on the reliability of the Twitch API at the time of collection.
### Purpose and Ethical Considerations:
This dataset is intended solely for a personal, non-profit data analysis project.
No commercial use or monetary gain is associated with this data.
No intention to disparage or diminish any streamer or language community is implied through this analysis.
Data handling and analysis will prioritize ethical considerations and respect for individual streamers.
### Additional Notes:
Twitch Terms of Service and API guidelines are observed for responsible data usage.
Any conclusions drawn from this analysis reflect observations within the dataset's scope and limitations.
Further research or data collection may be necessary to validate findings or expand scope.

## <u style="font-size: 1.5rem;">Project Structure:</u>
<ul>
  <li>
    <strong>Data Cleaning</strong>
    <ul>
      <li>Gender Prediction - (As twitch does not have a way to know streamers genders, this folder is to deal with it using flask)</li>
        <ul>
          <li>output/</li>
          <li>static/
            <ul>
              <li>css/</li>
              <li>js/</li>
            </ul>
          </li>
          <li>templates/</li>
        </ul>
      </li>
      <li>Visualizations</li>
      <li>__pycache__/</li>
      <li>data_transformations_functions.py (custom functions to help clean the data)</li>
    </ul>
  </li>

  <li>
    <strong>Data Collection</strong>
    <ul>
      <li>database_manager.py(script responsible for saving the data into ibm db2 database)</li>
      <li>web_scraping.py (script responsible for retrieving the data from twitch and pre cleaning with bs4)</li>
      <li>data/</li>
      <li>fails_storage/ (This folder is responsible when the db2 database can't save the data, so instead of throwing it out, it saves on a txt file, and try again later.)</li>
      <li>
        utils/
        <ul>
          <li>chrome_driver/ (chrome_driver is a necessary file to use selenium python library)</li>
          <li>database_schema.txt (schema of the db2 database)</li>
        </ul>
      </li>
      <li>__pycache__/</li>
    </ul>
  </li>

  <li>
    <strong>twitch_data_analysis.ipynb (main notebook data analysis) </strong>
  </li>
</ul>

## <u style="font-size: 1.5rem;">How to run the project:</u>

1. I suggest using Python 3.10, as newer versions of ibm_db might not be compatible.
2. Open a terminal or command prompt in the project's root directory.
3. Install Pipenv (if needed) "pip install pipenv"
4. Install Dependencies "pipenv install --dev"
5. Activate Virtual Environment "pipenv shell"
1. In data_collection/config.json put your db2 database credentials
2. Run web_scraping.py
3. After getting the data into the db2 database download th tables as csv file
4. Get all the streamers names using pandas from streamers.csv
5. With all_streamers.txt in hands, use the gender_prediction module to manually get the streamers gender
6. Finally, Run the twitch_data_analysis.ipynb notebook

  
