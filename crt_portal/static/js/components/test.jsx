'use strict';

class LikeButton extends React.Component {
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
  }
}

const domContainer = document.querySelector('#react_container');
const root = ReactDOM.createRoot(domContainer);
root.render(<LikeButton />);
