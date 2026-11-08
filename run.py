from carebot import create_app
app = create_app()

if __name__ == "__main__":
    # Debug is disabled by default. Use Flask CLI for local development.
    app.run(host="127.0.0.1", port=5000, debug=False)
