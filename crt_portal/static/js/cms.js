(function(root, dom) {
  let updateCount = 0;
  let updateAborter = null;

  function renderMarkdown(component) {
    updateCount++;
    if (updateAborter) updateAborter.abort(); // Cancel other pending requests
    updateAborter = new AbortController();
    const updateCountBeforePost = updateCount;
    window
      .fetch('/cms/render', {
        method: 'POST',
        signal: updateAborter.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': Cookies.get('csrftoken')
        },
        mode: 'same-origin',
        body: JSON.stringify({ entry: component.props.entry })
      })
      .then(response => {
        updateAborter = null;
        response.text().then(text => {
          if (updateCount !== updateCountBeforePost) return;
          component.setState({ html: text });
        });
      })
      .catch(error => {
        console.error(error);
      });
  }

  const TemplatePreview = createClass({
    getInitialState() {
      return { html: '' };
    },
    componentDidMount() {
      renderMarkdown(this);
    },
    componentDidUpdate(previousProps) {
      if (
        previousProps.entry.get('data')?.get('body') ===
          this.props.entry.get('data')?.get('body') &&
        previousProps.entry.get('data')?.get('is_html') ===
          this.props.entry.get('data')?.get('is_html')
      ) {
        return;
      }
      renderMarkdown(this);
    },
    render() {
      return h('div', { dangerouslySetInnerHTML: { __html: this.state.html } });
    }
  });

  CMS.registerPreviewTemplate('response_templates', TemplatePreview);
})(window, document);
