import fauxfactory
from wait_for import wait_for

from mta.entities.analysis_configuration import AnalysisConfiguration
from mta.entities.analysis_results import AnalysisResultsView


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
    analysis_configuration = AnalysisConfiguration(application, project_name)
    analysis_configuration.delete_application("arit-ear-0.8.1-SNAPSHOT.ear")
    # Verify that analysis completes
    view = analysis_configuration.create_view(AnalysisResultsView)
    view.wait_displayed()
    assert view.is_displayed
    wait_for(lambda: view.analysis_results.in_progress(), delay=0.6, timeout=450)
    wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
    assert view.analysis_results.is_analysis_complete()
    project.delete()
