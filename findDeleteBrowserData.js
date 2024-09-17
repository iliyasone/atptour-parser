function findDeepElement(selector, text) {
    let elems = document.querySelectorAll('*');
    for (let elem of elems) {
        let found = searchShadowRoot(elem, selector, text);
        if (found) return found;
    }
    return null;
}

function searchShadowRoot(root, selector, text) {
    if (root.shadowRoot) {
        let found = Array.from(root.shadowRoot.querySelectorAll(selector)).find(e => e.textContent.trim() === text);
        if (found) return found;
        
        // Recursively search within deeper shadow roots
        let shadowChildren = root.shadowRoot.querySelectorAll('*');
        for (let child of shadowChildren) {
            found = searchShadowRoot(child, selector, text);
            if (found) return found;
        }
    }
    return null;
}

return findDeepElement('#label', 'Delete browsing data');
