"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import fauxfactory

from mta.entities.analysis_results import AnalysisResults
from mta.entities.analysis_results import AnalysisResultsView


def test_analysis_results_search_sort_delete(request, mta_app):
    """Test search and sort analysis

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project
            2. Run the analysis
            3. Go to Analysis results page and search analysis by ID or status
            4. Delete analysis and  search analysis by ID or status
        expectedResults:
            1. All the analysis rows should get collected which matched ID or status from search
               value
            2. Deleted analysis results should not appear on analysis results page
    """
    # TODO(ghubale): Sort analysis is not covered in automation
    # TODO(ghubale): Search analysis by status is not covered in automation
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = mta_app.collections.projects
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
    request.addfinalizer(project.delete_if_exists)
    analysis_results = AnalysisResults(mta_app, project_name)
    analysis_results.run_analysis()
    view = analysis_results.create_view(AnalysisResultsView)
    view.wait_displayed("30s")
    # search row 1 in list
    analysis_results.search_analysis(row=1)
    assert view.analysis_row(row=1).analysis_number.is_displayed
    view.clear_search()
    view.wait_displayed("30s")
    # search row 2 in list
    analysis_results.search_analysis(row=2)
    view.clear_search()
    view.wait_displayed("30s")
    # Sort Analysis
    analysis_results.sort_analysis()
    assert analysis_results.get_analysis_number(view, row=1) < analysis_results.get_analysis_number(
        view, row=2
    )
    view.wait_displayed("30s")
    # delete analysis of row 1
    analysis_results.delete_analysis(row=1)
    # Cancel delete operation of remaining analysis row
    view.wait_displayed("30s")
    analysis_results.delete_analysis(row=1, cancel=True)
