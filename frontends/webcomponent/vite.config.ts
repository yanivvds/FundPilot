import { defineConfig } from 'vite';
import path from 'path';
import fs from 'fs';

// Serve the root /img/ folder during Vite dev & preview so that
// absolute paths like /img/empty-first-query.svg resolve correctly
// (in production the Flask app handles this via static file serving).
const serveRootImgPlugin = {
  name: 'serve-root-img',
  configureServer(server: any) {
    const rootImgDir = path.resolve(__dirname, '../../img');
    server.middlewares.use('/img', (req: any, res: any, next: any) => {
      const filePath = path.join(rootImgDir, req.url);
      if (fs.existsSync(filePath)) {
        const ext = path.extname(filePath).toLowerCase();
        const mimeTypes: Record<string, string> = {
          '.svg': 'image/svg+xml',
          '.png': 'image/png',
          '.jpg': 'image/jpeg',
          '.jpeg': 'image/jpeg',
          '.webp': 'image/webp',
        };
        res.setHeader('Content-Type', mimeTypes[ext] ?? 'application/octet-stream');
        fs.createReadStream(filePath).pipe(res);
      } else {
        next();
      }
    });
  },
  configurePreviewServer(server: any) {
    const rootImgDir = path.resolve(__dirname, '../../img');
    server.middlewares.use('/img', (req: any, res: any, next: any) => {
      const filePath = path.join(rootImgDir, req.url);
      if (fs.existsSync(filePath)) {
        const ext = path.extname(filePath).toLowerCase();
        const mimeTypes: Record<string, string> = {
          '.svg': 'image/svg+xml',
          '.png': 'image/png',
          '.jpg': 'image/jpeg',
          '.jpeg': 'image/jpeg',
          '.webp': 'image/webp',
        };
        res.setHeader('Content-Type', mimeTypes[ext] ?? 'application/octet-stream');
        fs.createReadStream(filePath).pipe(res);
      } else {
        next();
      }
    });
  },
};

export default defineConfig({
  plugins: [serveRootImgPlugin],
  define: {
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __BUILD_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
  },
  build: {
    outDir: 'dist',
    lib: {
      entry: 'src/index.ts',
      formats: ['es'],
      fileName: () => 'vanna-components.js',
    },
    rollupOptions: {
      // Remove external to bundle lit with the components
      // external: /^lit/,
    },
  },
  preview: {
    port: 9876,
    strictPort: true,
  },
});
