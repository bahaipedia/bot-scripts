# botscripts
There are two folders of scripts, one for Pywikibot and another for WikibaseIntegrator.

Pywikibot is suitable for performing bulk editing actions on Bahaipedia, Bahai.works and those related wiki's. 

WikibaseIntegrator is intended for use with Wikibase style websites like Bahaidata.org or Wikidata.org. 

# Installing Pywikibot




# Installing WikibaseIntegrator

Follow the steps below to install and set up WikibaseIntegrator.

### 1. Create a Virtual Environment

Navigate to your project directory and run:

```bash
python -m venv wikibase_env
```

### 2. Activate the Virtual Environment

- **Windows**:
  ```bash
  wikibase_env\Scripts\activate
  ```

- **Linux**:
  ```bash
  source wikibase_env/bin/activate
  ```

### 3. Install WikibaseIntegrator

Run the following command to install WikibaseIntegrator:

```bash
python -m pip install wikibaseintegrator
```

### 4. Verify the Installation

To verify that WikibaseIntegrator has been installed correctly, run:

```bash
python -c "import wikibaseintegrator; print(wikibaseintegrator.__version__)"
```
