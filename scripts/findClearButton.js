function findDeepElement(selector) {
    let elems = document.querySelectorAll('*');
    for (let elem of elems) {
        let found = searchShadowRoot(elem, selector);
        if (found) return found;
    }
    return null;
}

function searchShadowRoot(root, selector) {
    if (root.shadowRoot) {
        let found = root.shadowRoot.querySelector(selector);
        if (found) return found;
        
        // Recursively search within deeper shadow roots
        let shadowChildren = root.shadowRoot.querySelectorAll('*');
        for (let child of shadowChildren) {
            found = searchShadowRoot(child, selector);
            if (found) return found;
        }
    }
    return null;
}

return findDeepElement('#clearButton');