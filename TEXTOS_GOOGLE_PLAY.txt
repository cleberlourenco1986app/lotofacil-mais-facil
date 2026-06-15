{
  "name": "lotofacil-mais-facil-mobile",
  "version": "1.0.0",
  "description": "App mobile Lotofacil + Facil",
  "private": true,
  "scripts": {
    "cap:add:android": "npx cap add android",
    "cap:sync": "npx cap sync android",
    "cap:open": "npx cap open android",
    "android": "npm run cap:add:android && npm run cap:sync && npm run cap:open"
  },
  "dependencies": {
    "@capacitor/android": "latest",
    "@capacitor/cli": "latest",
    "@capacitor/core": "latest"
  },
  "devDependencies": {}
}
