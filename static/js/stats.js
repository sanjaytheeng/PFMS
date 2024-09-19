// Function to render a chart with specified type, data, and labels
const renderChart = (type, data, labels, ctxId, title) => {
    var ctx = document.getElementById(ctxId).getContext("2d");
    new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: "Expenses",
                data: data,
                backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(255, 206, 86, 0.2)",
                    "rgba(201, 203, 207, 0.2)",
                    "rgba(54, 162, 235, 0.2)"
                ],
                borderColor: [
                    "rgba(255, 99, 132, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(201, 203, 207, 1)",
                    "rgba(54, 162, 235, 1)"
                ],
                borderWidth: 1
            }]
        },
        options: {
            title: {
                display: true,
                text: title
            },
            responsive: true,
            maintainAspectRatio: true,
        }
    });
};

// Function to handle fetching data and rendering charts
const getChartData = () => {
    console.log("Fetching data...");
    fetch('expense_category_summary')
        .then((res) => res.json())
        .then((results) => {
            console.log("Results:", results);
            const category_data = results.expense_category_data;
            const labels = Object.keys(category_data);
            const data = Object.values(category_data);

            // Render Pie Chart
            renderChart('pie', data, labels, 'pieChart', 'Expense per Category (Pie Chart)');

            // Render Bar Chart
            renderChart('bar', data, labels, 'barChart', 'Expense per Category (Bar Chart)');

            renderChart('line', data, labels, 'lineChart', 'Expense per Category (Line Chart)');

            renderChart('polarArea', data, labels, 'polarChart', 'Expense per Category (PolarArea Chart)');
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });
};

// Add event listener for document load
document.addEventListener('DOMContentLoaded', getChartData);
