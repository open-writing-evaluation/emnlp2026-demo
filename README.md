# Chinese GEC Applications for L2 Learning
This repository hosts links to the web and mobile applications introduced by the paper **Chinese GEC Applications Supporting L2 Writing from Translation-Based to Immersive Learning**. Submitted to *EMNLP 2026 System Demonstrations*.

## Requirements
The applications consist of a backend (server-side) which processes the input sentences and generates corrections, as well as front end interfaces for the user to interact with. For demonstration purposes, we designed this code release to work specifically with a serverless setup all using localhost. 

### Unified Backend
The mobile and web applications share one backend for compact code integration, resource sharing, and convenient server deployment. The backend was built with the web framework Flask using Python.

First install [Python](https://www.python.org/) (latest recommended, software was developed on [Python 3.11.5](https://www.python.org/downloads/release/python-3115/)) and the corresponding dependencies:
```
# Install dependencies (we recommend setting up an environment with venv or conda)
python -m pip install -r requirements.txt
``` 
#### ERRANT 
A modified version of our ERRANT toolkit, [jp-errant](https://github.com/open-writing-evaluation/jp-errant-bea), is included in this repository. This does not require a separate installation. However, testers need to place the file character table ```triplet_no_dup_threshold.csv``` in the following directory:
```
/jp_errant/zh/triplet_no_dup_threshold.csv
```
A compressed file is already in the directory, simply run the following
```
cd jp_errant/zh
tar -xvf triplet_no_dup_threshold.tar.gz
cd ../..
```
#### Question Bank
Next, to setup the question bank, extract the file
```
tar -xvf trimmed_questions.tar.gz
```
#### Models
Lastly, extract the trained models [trained_models.tar.gz]()
```
tar -xvf trained_models.tar.gz
```

When everything is in place, your directory should resemble the following:
```
project/
│
└───jp_errant/
│       └───zh/
│           └───triplet_no_dup_threshold.csv
└───trained_models/
│
└───trimmed_questions/
│
└───app.py
│
└───API_Config.py
│   ...
```
#### LLM API
Access to an LLM API is required for the applications. The codebase utilizes Python's requests library for HTTP POST requests to query the LLM to ensure wide compatibility. Please use your personal API key or try to obtain a key from a free service for testing purposes. Add your key by modifying the file, ***API_Config.py***, as shown in the example below:
```
# Sample Contents of API_Config.py
api_config  = {
    'url': "https://openrouter.ai/api/v1/chat/completions",
    'model': "deepseek/deepseek-chat-v3-0324",
    'key' : "Bearer YOUR_API_KEY_HERE"
}
``` 
#### Launch the Backend
Once you reach this step you've successfully setup the backend (local) server. To start the service, simply run:
```
python app.py
```
This will start the Flask server. Server start or restarts may take a certain amount of time due to the process of loading trained models into memory. 
*Note: Your initial run will result in automatic torch model downloads from huggingface, please ensure stable internet access for this process.*
### Front End (Web)
The web application is designed to operate in any browser environment with essentials such as active scripting (JavaScript), HTTP requests, and CSS enabled. 

For the best experience, we recommend using the latest versions of browsers such as Chrome and Mozilla Firefox.

### Front End (Mobile)
The mobile application is built to run in Android environments. The application requires Android operating systems versioned Android 7.0 and above (SDK 24). The application was tested on Android 14 and 15 during development. 

The specific APK installable provided by this release was built to work with the assumption that the backend service is running on localhost. Hence, we recommend using the Official Android emulator in [Google's Android Studio IDE](https://developer.android.com/studio). Please read the [instructions here](https://developer.android.com/studio/run/emulator) on using the Android emulator. We recommend this [guide here](https://developer.android.com/studio/run/managing-avds), which showcases the steps needed to setup and start a virtual device.

#### Emulator Device Settings
The application was designed to run on a wide range of mobile devices without much constraints on performance as the compute heavy tasks are handled by the backend server. 
Here we list our recommended settings for testing:
<table>
  <tr>
    <th>Android API</th>
    <td>API Level 35; Android 15</td>
  </tr>
  <tr>
    <th>Form factor</th>
    <td>Medium Phone</td>
  </tr>
  <tr>
    <th>CPU Cores</th>
    <td>4 - 6 Cores</td>
  </tr>
  <tr>
    <th>RAM</th>
    <td>4 - 6 GB</td>
  </tr>
    <tr>
    <th>Storage</th>
    <td>8 GB</td>
  </tr>
</table>

</br>

***Application installation will be detailed in the following sections.***

### *<span style="color:red">Ensure the backend has fully started before accessing the applications!</span>*

## Web Application (*Write it Right!*)
### Access Link
Once the backend service has started, you will see a message similar to the following in your terminal from Flask:
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.23.35.143:5000
```
Simply click on the link (e.g. http://127.0.0.1:5000), to start the web application.
### Usage Instructions
The following section will briefly introduce the application's UI and features.

1. Upon entering the website, users will be greeted by a text box where they can begin writing.
    - The web application supports grammar error corrections for Chinese text in paragraph form.
2. Users can press submit to obtain grammar error corrections. 
    - A loading spinner will appear the interim while the system completes its analysis. 
3. Once the processing is complete, the results will appear in a section below the input text box. 
    - The results section will present the corrections in the format of an annotated sentence, where deletions and insertions are highlighted in red and green, respectively.
    - Users could opt to press to "Hide Annotations" button, to display a clean version of the corrected sentence without the colored highlights. In addition, users can press the same button, now "Show Annotations", to view the annotated version again.
### Screen Captures
<table>
    <tr>
        <td align="center">Annotated Results</td>
        <td align="center">Corrected Results</td>
    </tr>
    <tr>
        <td align="center"><img src="https://github.com/user-attachments/assets/f54ef6c4-d7cb-448b-bfda-82e0a31f2689" alt="web_app_anno" width = 100% height = 100%></td>
        <td align="center"><img src="https://github.com/user-attachments/assets/90af99b1-bf39-4678-af56-9455c82cfc40" alt="web_app_corr" width = 100% height = 100%></td>
    </tr> 
</table>

## Mobile Application (*Translate it Right!*)

### Access Link
Please use the following hyperlink to download the [APK file](https://drive.google.com/file/d/1SbCJH4z1iXmEipEmvT5d1NLU4dZFUoKl/view?usp=sharing) (Google Drive Link).

APK files are installer files native to Android. To install our application, please follow these steps:
1. Download the APK file via the aforementioned link.
2. Assuming you have created a virtual device ([guide here](https://developer.android.com/studio/run/managing-avds)), start your Android emulator in Android studio by clicking the play icon in Device Manager.
3. Simply drag and drop the APK file to the emulator, and the application should install automatically. Refer to the [following guide](https://developer.android.com/studio/run/emulator-install-add-files) for details on installation.
### Usage Instructions
The following section will briefly introduce the application's UI and features.
1. Language Selection
    - Users are prompted to first select an exercise language (i.e. the language they want to practice) and a feedback language (i.e. the language they are familiar with). 
    - The mobile application currently supports English -> Chinese and Chinese -> English translation exercises.
2. Translation Exercise
    - Users will be presented with a sentence sourced from a question bank in their chosen feedback language.
    - Users will try to translate the given sentence, and type their answer in the available text field.
    - Users could use the refresh button to switch to another exercise sentence.
3. Exercise Results
    - After pressing "Submit", users will be taken to the "Results" screen after the server backend completes its analysis. In the interim, users will be greeted by a loading screen. 
    - The "Results" screen contains three sections: (i) the input sentence (the user's answer), (ii) the annotated sentence, where deletions and insertions are highlighted in red and green, respectively, and (iii) LLM feedback to provide guidance based on the errors made in the user's answer. 
    - Users can choose to either start a new exercise or save the current exercise. 
4. Exercise History
    - Contains a list view of saved exercises.
    - Users can swipe left 
to bring up a modal view that includes the details of each saved entry or swipe right to delete the entry from exercise history.
    - Users could also utilize the "Clear History" button to delete all exercise history.
### Screen Captures

<table>
    <tr>
        <td align="center">Language Selection</td>
        <td align="center">Translation Exercise</td>
        <td align="center">Input Screen</td>
    </tr>
    <tr>
        <td align="center"><img src="https://github.com/user-attachments/assets/cfc52bf2-8834-414c-81df-dae5a444a52a" alt="select_lang" width = 80% height = 80%></td>
        <td align="center"><img src="https://github.com/user-attachments/assets/28ecf70a-e96c-40fa-8c73-a17178678246" alt="question" width = 80% height = 80%></td>
        <td align="center"><img src="https://github.com/user-attachments/assets/c2f65778-624d-4397-b3a5-e46486ab5c7d" alt="input" width = 80% height = 80%></td>
    </tr>
    <tr>
        <td align="center">Exercise Results</td>
        <td align="center">Exercise History</td>
        <td align="center">History Modal</td>
    </tr>
    <tr>
        <td align="center"><img src="https://github.com/user-attachments/assets/44787bbb-76ea-4cfb-a7a8-07201222d566" alt="output" width = 80% height = 80%></td>
        <td align="center"><img src="https://github.com/user-attachments/assets/96c25091-21af-40f6-8367-c996866fa3a6" alt="history_list" width = 80% height = 80%></td>
        <td align="center"><img src="https://github.com/user-attachments/assets/1be11492-bf71-41a5-b043-6734488cbfec" alt="history_modal" width = 80% height = 80%></td>
    </tr>
</table>


## Demo Video
Click the [link here](https://youtu.be/XvkQKiO0PaQ) for a demo video showcasing both applications (web and mobile).

