const baseURL = 'http://localhost:8000';
let variants;

$(function () {
    getVariants().then((response) => {
        if (response.success) {
            variants = response.variants;
        }
    });

    sendMessage('Вы загадали животное ' + variants[0] + '?');
});

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
    return $.ajax(baseURL + '/variants', {
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
    return $.ajax(baseURL + '/variants/scheme', {
        type: 'get',
        async: true
    });
}
