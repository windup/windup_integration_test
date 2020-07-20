import fauxfactory

from mta.entities.analysis_results import AnalysisResults


def test_analysis_results(application):
    """ Validates Web console Test 03
    1) Upload more than one application into a project to analyse
    2) Delete one application and analyse
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=[
            "acmeair-webapp-1.0-SNAPSHOT.war",
            "arit-ear-0.8.1-SNAPSHOT.ear",
            "cadmium-war-0.1.0.war",
        ],
        transformation_path="Containerization",
    )
    assert project.exists

    analysis_results = AnalysisResults(application, project_name)
    analysis_results.run_analysis()
    # TODO : delete application and analyse
