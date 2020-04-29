var el = x => document.getElementById(x);


var ctx = document.getElementById('chart').getContext('2d');

function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function showChart(chartData, labels) {
  var options = {scales: {
                  yAxes:[{
                    ticks: {
                      beginAtZero: true,
                      max: 100,
                    }
                  }]
                }
              }

  var myBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        data: chartData,
        label: '%',
        backgroundColor: [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)'
        ],
        borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1
    }]

    },
    options: options
});
}

function analyze() {
  var self = this;
  var toAnalyze = el("analyze-text").value;
  console.log(toAnalyze)
  var classes = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
  var response = {'result': ['toxic', 'severe_toxic', 'obscene'], 'perc': [50, 40, 20, 10, 70, 60]}
  self.showChart(response['perc'], classes);
  return false;
  // if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {
    if (this.readyState === 4) {
      var classes = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
      console.log(e);
      var response = JSON.parse(e.target.responseText);

      self.showChart(response['perc'], classes);
      // el("result").innerHTML = `Result = ${response["result"]}\n(Confidence: ${response["perc"]}%`;
    }
    el("analyze-button").innerHTML = "Analyze";
  };

  var fileData = new FormData();
  fileData.append("text", toAnalyze);
  xhr.send(fileData);
}

