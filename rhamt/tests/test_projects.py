import fauxfactory


def test_project(application):
    project_name = fauxfactory.gen_alphanumeric(start="project_")
    project_collection = application.collections.projects
    # TO DO paramterize the test later for file_name and trans_path, hardcoding for now
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        file_name="acmeair-webapp-1.0-SNAPSHOT.war",
        transformation_path="Containerization",
    )
    assert project.exists(project_name)
