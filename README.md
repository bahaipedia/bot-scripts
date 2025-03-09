# botscripts
There are two folders of scripts, one for Pywikibot and another for WikibaseIntegrator.

Pywikibot is suitable for performing bulk editing actions on Bahaipedia, Bahai.works and those related wiki's. 

WikibaseIntegrator is intended for use with Wikibase style websites like Bahaidata.org or Wikidata.org. 

## Installing Pywikibot




## Installing WikibaseIntegrator

Follow the steps below to install and set up WikibaseIntegrator.

#### 1. Create a Virtual Environment

Navigate to your project directory and run:

```bash
python -m venv wikibase_env
```

#### 2. Activate the Virtual Environment

- **Windows**:
  ```bash
  wikibase_env\Scripts\activate
  ```

- **Linux**:
  ```bash
  source wikibase_env/bin/activate
  ```

#### 3. Install WikibaseIntegrator

Run the following command to install WikibaseIntegrator:

```bash
python -m pip install wikibaseintegrator
```

#### 4. Verify the Installation

To verify that WikibaseIntegrator has been installed correctly, run:

```bash
python -c "import wikibaseintegrator; print(wikibaseintegrator.__version__)"
```

### 5. Download the Scripts You Need

To download the specific bot scripts you need, navigate to the [wikibaseintegrator folder](https://github.com/bahaipedia/bot-scripts/tree/main/wikibaseintegrator) in the repository. You can download individual scripts by selecting them and clicking on the **Download** button or by cloning the entire repository.

For example, to download `import-articles.py`:

1. Visit the [import-articles.py file](https://github.com/bahaipedia/bot-scripts/blob/main/wikibaseintegrator/import-articles.py).
2. Right-click on **Raw** and select **Save Link As**.

### 6. Run the scripts

```bash
python path/to/import-articles.py
```
