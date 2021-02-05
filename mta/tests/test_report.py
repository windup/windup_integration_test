from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView


def test_send_feedback(create_minimal_project):
    """
    Test send feedback
    """
    project, project_collection = create_minimal_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.send_feedback.click()
