# Finance

Create a local Python virtual environment and install `requirements.txt`, then run `streamlit run app.py`.

Configure `MONGO_URI` through Streamlit deployment secrets or an ignored local `.streamlit/secrets.toml`. Keep database credentials and virtual environments out of Git.

The previously committed MongoDB password must be rotated in MongoDB Atlas. Removing the tracked file does not remove its older Git history; rotate the password before arranging history cleanup.
