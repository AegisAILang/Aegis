import os
import json

class AegisPackageManager:
    """Handles package management for AegisLang, including dependency installation and module tracking."""

    PACKAGE_DIR = "./aegis_packages"
    CONFIG_FILE = "aegis.json"

    def __init__(self):
        """Initializes the package manager and ensures package directory exists."""
        if not os.path.exists(self.PACKAGE_DIR):
            os.makedirs(self.PACKAGE_DIR)

    def create_project(self, project_name):
        """Creates a new AegisLang project with a package config file."""
        project_path = os.path.join(self.PACKAGE_DIR, project_name)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            config_path = os.path.join(project_path, self.CONFIG_FILE)
            with open(config_path, "w") as config_file:
                json.dump({"name": project_name, "dependencies": {}}, config_file, indent=4)
            return f"Project '{project_name}' created successfully."
        else:
            return f"Project '{project_name}' already exists."

    def install_package(self, project_name, package_name, package_version="latest"):
        """Installs a package for a given AegisLang project."""
        project_path = os.path.join(self.PACKAGE_DIR, project_name)
        config_path = os.path.join(project_path, self.CONFIG_FILE)

        if not os.path.exists(config_path):
            return f"Project '{project_name}' does not exist. Create it first."

        # Load current dependencies
        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

        # Add new package
        config_data["dependencies"][package_name] = package_version

        # Save updated config
        with open(config_path, "w") as config_file:
            json.dump(config_data, config_file, indent=4)

        return f"Package '{package_name}@{package_version}' installed for project '{project_name}'."

    def list_dependencies(self, project_name):
        """Lists all installed dependencies for a project."""
        project_path = os.path.join(self.PACKAGE_DIR, project_name)
        config_path = os.path.join(project_path, self.CONFIG_FILE)

        if not os.path.exists(config_path):
            return f"Project '{project_name}' does not exist."

        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

        return config_data.get("dependencies", {})