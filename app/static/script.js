function copyToClipboard(element) {
    var code = element.nextElementSibling.innerText;
    var textarea = document.createElement('textarea');
    textarea.value = code;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    element.textContent = 'Copied!';
    setTimeout(() => element.textContent = 'Copy', 2000);
}