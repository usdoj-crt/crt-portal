'use strict';

class RelatedReports extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: 0,
      error: false
    }
    };

  componentDidMount() {
    this.fetchTotalResults('/api/responses/');
  }

  fetchTotalResults = api => {
    fetch(api)
      .then(result => result.json())
      .then(count => this.setState({ data: count.count }))
      .catch(error => this.setState({ error }));
  };

  render() {
    if (this.state.data.length === 0) {
      return <h2 className="h3">Loading data...</h2>;
    } else if (!this.state.error) {
      return <h2 className="h3">Data loaded! {this.state.data}</h2>;
    } else if (this.state.error) {
      return <h2 className="h3">{this.state.error}</h2>
    }


    // Replicate this template: 
//     <table class="usa-table usa-table--borderless related-reports width-full">
//     <tbody>
//         {% for report in reports %}
//             <tr>
//                 <td>{{report.public_id}}</td>
//                 <td>{{report.assigned_section}}</td>
//                 <td>
//                     {% if report.recent_email_sent %}
//                     <span class="usa-tooltip" data-position="bottom" title="{{report.recent_email_sent}}">
//                         Letter sent
//                         <img src="{% static "img/ic_help-circle-dark.svg" %}" alt="More info" class="letter-sent-icon">
//                     </span>
//                     {% endif %}
//                 </td>
//                 <td>{{report.create_date|date:"SHORT_DATE_FORMAT"}}</td>
//             </tr>
//         {% endfor %}
//     </tbody>
// </table>



  }
}

const domContainer = document.querySelector('#react_container');
const root = ReactDOM.createRoot(domContainer);
root.render(<RelatedReports />);