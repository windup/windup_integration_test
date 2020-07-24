import fauxfactory

from mta.entities.analysis_results import AnalysisResults
from mta.entities.analysis_results import AnalysisResultsView


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
    analysis_results.search_analysis(row=1)
    # Verify that correct search results are displayed
    view = analysis_results.create_view(AnalysisResultsView)
    assert view.analysis_number_1.is_displayed
    analysis_results.search_analysis(row=2)
    assert view.analysis_number_2.is_displayed
    # TODO : delete application and analyse
