
export const msg = (type, body= null) => {
    if (typeof type !== 'string') {
        throw new TypeError('invalid message type');
    }
    const m = { type };
    if (body) {
        m.body = body;
    }
    return JSON.stringify(m);
};
