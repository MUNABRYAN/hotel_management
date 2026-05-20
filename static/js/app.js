const configAutoNumeric = {
    digitGroupSeparator: '.',
    decimalCharacter: ',',
    decimalCharacterAlternative: '.',
    decimalPlaces: 2,
    emptyInputBehavior: 'zero',
    modifyValueOnWheel: false,
};

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.input-moneda').forEach(input => {
        new AutoNumeric(input, configAutoNumeric);
    });
});

function getAutoNumericValue(elemento) {
    return AutoNumeric.getAutoNumericElement(elemento).getNumber() || 0;
}

function formatoNumeroLocal(numero) {
    return AutoNumeric.format(numero, configAutoNumeric);
}