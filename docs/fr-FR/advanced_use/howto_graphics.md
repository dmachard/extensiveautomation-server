---
name: How to add charts in report
---

# How to add charts in report

* [Purpose](howto_graphics#purpose)
* [Adding a chart in test report](howto_graphics#adding-a-chart-in-test-report)

## Purpose

This feature enables to add charts in test report. Collects some data during the run of your test and display them in the test report with charts.

## Adding a chart in test report

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Initialize the ChartJS library in the prepare section of your test

    ```python
    self.LIB_CHART = SutLibraries.Media.ChartJS(parent=self, name=None, debug=False)
    ```

3. Generate some fake data

    ```python
    labelsAxes = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
    dataA = [12, 19, 3, 5, 2, 3]
    dataB = [22, 49, 3, 5, 23, 3]
    legendDatas = ["tets", "test"]
    backgroundColor = '#4BC0C0'
    borderColor = '#36A2EB'
    ```
    
4. Generate the chart and put-it to the step 

    ```python
    myChart = self.LIB_CHART.barChart(
                                        labelsAxes=labelsAxes, 
                                        datas=[dataA, dataB], 
                                        legendDatas=legendDatas, 
                                        width=400, 
                                        height=300,
                                        backgroundColors=[borderColor, backgroundColor], 
                                        borderColors=[borderColor, backgroundColor],
                                        chartTitle="test"
                                    )
    self.step1.setPassed(actual="chart", chart=myChart)
    ```
    
5. Go the test archives and load the test report, the chart will appears on the report.

    ![](/docs/images/report_chart.png)

