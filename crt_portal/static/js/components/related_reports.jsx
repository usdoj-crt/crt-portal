'use strict';

class RelatedReports extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: 0,
      error: false
    };
  }

  componentDidMount() {
    this.fetchTotalResults('/api/related-reports/?email=rrose@example.com');
  }

  fetchTotalResults = api => {
    fetch(api)
      .then(result => result.json())
      .then(res => this.setState({ data: res }))
      .catch(error => this.setState({ error }));
  };

  render() {
    return (
      <>
        <h2>{this.props.title}</h2>
        {this.state.error ? (
          <>
            <p>I'm sorry, an error was encountered while returning the data.</p>{' '}
            <p>{this.state.error}</p>
          </>
        ) : (
          <table class="usa-table usa-table--borderless related-reports width-full">
            <tbody>
              {this.state.data === 0 ? (
                <p>Loading...</p>
              ) : (
                this.state.data.map((item, k) => {
                  <tr key={k}>
                    <td>{item.public_id}</td>
                    <td>{item.assigned_section}</td>
                    <td>
                      {item.recent_email_sent ? (
                        <span
                          class="usa-tooltip"
                          data-position="bottom"
                          title={item.recent_email_sent}
                        >
                          Letter sent
                          <img src={this.props.icon} alt="More info" class="letter-sent-icon" />
                        </span>
                      ) : null}
                    </td>
                    <td>{item.create_date}</td>
                  </tr>
                })
              )}
            </tbody>
          </table>
        )}
      </>
    );
  }
}

const domContainer = document.querySelector('#related_reports');
const root = ReactDOM.createRoot(domContainer);
root.render(<RelatedReports title="Total Complaints" icon="img/intake-icons/copy.svg" />);
