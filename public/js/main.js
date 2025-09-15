const baseURL = 'http://localhost:8000';
let variants = [];
let answer;
let first = true;
$(function () {
    getVariants().then((response) => {
        response = JSON.parse(response);
        if (response.success) {
            variants = response.variants;
            $('#start-game').on('click', function () {
                $(this).hide();
                let $answerButtons = $('.answer-btn');
                $answerButtons.show();

                variants.forEach(function (variant, index) {

                    console.log(variant);

                    if (first === true) {
                        first = false;
                        sendMessage('Вы загадали животное ' + variant.name + '?');
                        $answerButtons.on('click', function () {
                            answer = $(this).val();
                            if (answer === variant.answer) {
                                win();
                            }
                        });
                        $answerButtons.off('click');
                    }

                    sendMessage(variant.question + '?');
                    $answerButtons.on('click', function () {
                        answer = $(this).val();
                        if (answer === variant.answer) {
                            $answerButtons.off('click');
                            sendMessage('Вы загадали животное ' + variant.name + '?');
                            $answerButtons.on('click', function () {
                                answer = $(this).val();
                                if (answer === variant.answer) {
                                    win();
                                }
                            });
                        }
                    });
                    $answerButtons.off('click');
                });

            });
        }
    });
});

function win() {
    sendMessage('Победа');
}

function sendMessage(message) {
    $('#message').text(message);
}

async function getVariants() {
    return $.ajax(baseURL + '/variants', {
        type: 'get',
        async: true
    });
}

async function storeVariant(variant) {
    return $.ajax(baseURL + '/variants/store', {
        type: 'post',
        async: true,
        data: {
            name: variant.name,
            question: variant.question,
            answer: variant.answer
        }
    });
}

async function detailsVariant(variant_id) {
    return $.ajax(baseURL + `/variants/${variant_id}`, {
        type: 'get',
        async: true
    });
}

async function showDB() {
    return $.ajax(baseURL + '/scheme', {
        type: 'get',
        async: true
    });
}
