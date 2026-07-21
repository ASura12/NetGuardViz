import http from 'k6/http';

export const options = {
    vus: 50,
    duration: '30s',
};

const params = {
    headers: {
        Authorization: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZXIxMjNAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3Nzg4NzQxODB9.5K_CzVHL6N4MJOIqcL3ypHPlkevgLXJ_JSViqUX9Kfg',
    },
};

export default function () {
    //http.get('http://127.0.0.1:8000/api/logs/', params);
    // http.get('http://127.0.0.1:8000/api/alerts/', params);
    http.get('http://127.0.0.1:8000/api/stats/', params);
}