odoo.define('adm.application.progress', require => {
    require('web.core');

    function updateProgressbarValue() {
        // Get the size of the ul
        const $nodeList = $('.progressbar ul li');
        const nodeLength = $nodeList.length;

        // Let's find the current node index
        let currentNodeIndex = 0;
        for (let i = 0; i < nodeLength; i++) {
            if ($nodeList[i].classList.contains('current')) {
                currentNodeIndex = i;
                break;
            }
        }
        // currentNodeIndex = 2;
        const $ul = $('.progressbar ul')
        let progressBarWidth = $ul[0].offsetWidth;
        let progressBarHeight = $ul.height();

        // Width of the container as max, and the current note position in px as value
        const currentNodePos = $nodeList[currentNodeIndex].offsetLeft + $nodeList[currentNodeIndex].offsetWidth/2;

        $('.progressbar progress').attr('max', progressBarWidth);
        initProgressbarAnimation(currentNodePos + 14);
    }

    function initProgressbarAnimation(maxValue) {
        let currentValue = 0;
        const $progressEl = $('.progressbar progress');
        let intervalId = setInterval(() => {
            currentValue += 4;
            if (currentValue > maxValue) {
                currentValue = maxValue;
                clearInterval(intervalId);
            }
            $progressEl.val(currentValue)
        }, 2);
    }

    $(document).ready(() => {
        updateProgressbarValue();
    });

});