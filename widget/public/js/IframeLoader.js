(function() {

    function createStyles() {
        const style = document.createElement('style');
        style.innerHTML = `
            .iframe-wrapper {
                border: solid 1px;
                border-radius: 5px;
                border-color: #FF8E93;
                width: 300px;
                height: 450px;
                position: absolute;
                display: flex;
                align-items: stretch;
                flex-flow: column;
                bottom: 0px;
                right: 0px;
                margin: 25px;
            }
            .iframe-wrapper-header {
                cursor: pointer;
                background-color: #FF8E93;
                height: 50px;
            }
            .iframe-wrapper > iframe {
                position: relative;
                height: 100%;
            }
            .widget-open-button {
                cursor: pointer;
                background-color: #FF8E93;
                width: 50px;
                height: 50px;
                border-radius: 50px;
                position: absolute;
                bottom: 0px;
                right: 0px;
                margin: 25px;
            }
        `;
        document.getElementsByTagName('head')[0].appendChild(style);
    }

    function createWidgetIframeWrapper() {
        const iframeWrapper = document.createElement("div");
        iframeWrapper.setAttribute("id", "iframe-wrapper")
        iframeWrapper.classList.add("iframe-wrapper");

        const iframeHeader = document.createElement("div");
        iframeHeader.addEventListener("click", createWidgetButton)
        iframeHeader.classList.add("iframe-wrapper-header");

        const iframe = document.createElement("iframe");
        iframe.setAttribute("frameBorder", "0");
        iframe.src = "http://localhost:3000/widget";

        iframeWrapper.appendChild(iframeHeader);
        iframeWrapper.appendChild(iframe);
        document.body.appendChild(iframeWrapper);
        destroyWidgetButton()
    }
    function destroyWidgetIframeWrapper() {
        const iframeWrapper = document.getElementById("iframe-wrapper")
        if (iframeWrapper)
            iframeWrapper.remove()
    }

    function createWidgetButton() {
        const widgetButton = document.createElement("div");
        widgetButton.setAttribute("id", "widget-open-button")
        widgetButton.classList.add("widget-open-button");
        widgetButton.addEventListener("click", createWidgetIframeWrapper)
        document.body.appendChild(widgetButton);
        destroyWidgetIframeWrapper()
    }
    function destroyWidgetButton() {
        const widgetButton = document.getElementById("widget-open-button")
        if (widgetButton)
            widgetButton.remove()
    }

    createStyles()
    createWidgetButton()
})();
