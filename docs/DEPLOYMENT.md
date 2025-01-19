# Deployment

I've deployed the application to Fly.io and it can be found at [mini-search-engine.fly.dev](mini-search-engine.fly.dev).

The supplied Dockerfile installs all of the native dependencies required (Rust, primarily, along with the Python base image), installs the application dependencies and then starts the web server as the primary entrypoint for the application.

To deploy the application, just run `fly deploy` from the root directory of the project and the CLI will use the supplied `fly.toml` file to spin up the environment. The file contains the environment variables for the application as well as the configuration for the persisted volume that houses the crawler output and the index.
