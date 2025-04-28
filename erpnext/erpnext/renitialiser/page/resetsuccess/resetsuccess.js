frappe.pages['resetsuccess'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'RESET SUCCESS',
        single_column: true
    });

    const urlParams = new URLSearchParams(window.location.search);
    const encodedData = urlParams.get('data');
    
    let response = {};
    try {
        response = JSON.parse(decodeURIComponent(encodedData));
    } catch (e) {
        response = { status: "error", message: "Failed to parse response data" };
    }

    let html = `
    <div class="reset-success-container">
        <div class="reset-success-card">
            <h3 class="reset-success-title">Reset Operation Result</h3>
            <div class="status-line ${response.status === 'success' ? 'success' : 'error'}">
                <strong>Status:</strong> ${response.status}
            </div>`;

    if (response.message) {
        html += `
            <div class="message-box">
                <strong>Message:</strong> ${response.message}
            </div>`;
    }

    if (response.results) {
        html += `
            <div class="results-section">
                <h4>Results:</h4>
                <ul class="results-list">`;
        for (const [doctype, message] of Object.entries(response.results)) {
            html += `
                    <li class="result-item">
                        <strong>${doctype}:</strong> ${message}
                    </li>`;
        }
        html += `
                </ul>
            </div>`;
    }

    html += `
        </div>
    </div>`;

    // Add CSS to the page
    $(page.body).html(html);
    $(`<style>
        .reset-success-container {
            display: flex;
            justify-content: center;
            padding: 20px;
            background-color: #f9f9f9;
            min-height: calc(100vh - 40px);
        }

        .reset-success-card {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 30px;
            max-width: 800px;
            width: 100%;
            color: #333333;
            border: 1px solid #dddddd;
        }

        .reset-success-title {
            color: #222222;
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 24px;
            border-bottom: 1px solid #eeeeee;
            padding-bottom: 10px;
        }

        .status-line {
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 16px;
        }

        .status-line.success {
            background-color: #e8f5e9;
            border-left: 4px solid #2e7d32;
            color: #2e7d32;
        }

        .status-line.error {
            background-color: #ffebee;
            border-left: 4px solid #c62828;
            color: #c62828;
        }

        .message-box {
            background-color: #f0f0f0;
            padding: 12px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #9e9e9e;
        }

        .results-section {
            margin-top: 25px;
        }

        .results-section h4 {
            color: #333333;
            margin-bottom: 15px;
            font-size: 18px;
        }

        .results-list {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }

        .result-item {
            padding: 10px 15px;
            margin-bottom: 8px;
            background-color: #f5f5f5;
            border-radius: 4px;
            border-left: 3px solid #bdbdbd;
            transition: background-color 0.2s;
        }

        .result-item:hover {
            background-color: #eeeeee;
        }

        .result-item strong {
            color: #000000;
        }
    </style>`).appendTo(page.body);
};
