import express from 'express';
import cors from 'cors';
import routes from './routes';
import { appConfig } from './config';
import { initDb } from './db';
import { notFoundHandler } from './middleware/notFoundHandler';
import { errorHandler } from './middleware/errorHandler';

const app = express();

app.use(cors({ origin: appConfig.corsOrigin, credentials: true }));
app.use(express.json({ limit: '5mb' }));

app.get('/', (_req, res) => {
    res.json({ message: 'DigiPraman backend is up', env: appConfig.env });
});

app.use('/api', routes);

app.use(notFoundHandler);
app.use(errorHandler);

const start = async () => {
    await initDb();
    app.listen(appConfig.port, () => {
        console.log(`🚀 Server listening on port ${appConfig.port}`);
    });
};

start().catch((error) => {
    console.error('Failed to start server', error);
    process.exit(1);
});

export default app;