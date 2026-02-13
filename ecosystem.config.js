module.exports = {
    apps: [
        {
            name: "iqlawd-api-v3",
            script: "python3",
            args: "-m uvicorn iq_lawd.api.server:app --host 0.0.0.0 --port 8000",
            cwd: "/root/iqlawd/backend",
            env: {
                DB_PATH: "/root/iqlawd/backend/iqlawd.db",
                PYTHONPATH: "/root/iqlawd/backend"
            }
        },
        {
            name: "iqlawd-ui-v3",
            script: "npm",
            args: "start",
            cwd: "/root/iq_lawd_v2/frontend_src",
            env: {
                PORT: 3005,
                NODE_ENV: "production"
            }
        }
    ]
};
