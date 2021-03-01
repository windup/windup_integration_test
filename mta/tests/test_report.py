from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView


def test_send_feedback(create_minimal_project):
    """Test send feedback

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: MTA
        testSteps:
            1. Create project and run analysis
            2. Click on report action to see detailed report
            3. Click on `Send Feedback` button
        expectedResults:
            1. It should open feedback window
    """
    project, project_collection = create_minimal_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.send_feedback.click()
