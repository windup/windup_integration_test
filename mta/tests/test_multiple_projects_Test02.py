import fauxfactory

from mta.entities.analysis_results import AnalysisResults
from mta.entities.applications import Applications


def test_multiple_applications_upload(request, application):
    """ Validates Web console Test 02
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
    applications = Applications(application, project_name)
    applications.delete_application("arit-ear-0.8.1-SNAPSHOT.ear")
    # Verify that analysis completes
    analysis = AnalysisResults(application, project_name)
    analysis.run_analysis()

    @request.addfinalizer
    def _finalize():
        project.delete()
