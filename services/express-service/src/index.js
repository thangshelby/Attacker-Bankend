import express from "express";
import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import { fileURLToPath } from "url";
import { dirname } from "path";
import bodyParser from "body-parser";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PROTO_PATH = __dirname + "../../base.proto";
const packageDefinition = protoLoader.loadSync(PROTO_PATH);
const baseProto = grpc.loadPackageDefinition(packageDefinition).base;

const client = new baseProto.BaseService(
  // "python-service:50051",
  "localhost:50051",
  grpc.credentials.createInsecure()
);

const app = express();
const port = 3000;
app.use(bodyParser.json());

app.get("/", (req, res) => {
  return res.send("asd");
});

app.get("/hello/:name", (req, res) => {
  console.log(req.params.name);
  client.SayHello({ name: req.params.name }, (err, response) => {
    if (err) return res.status(500).send(err);
    res.send(response.message);
  });
});
app.get("/bye/:name", (req, res) => {
  console.log(req.params.name);
  client.SayGoodBye({ name: req.params.name }, (err, response) => {
    if (err) return res.status(500).send(err);
    res.send(response.message);
  });
});

app.listen(port, () => {
  console.log(`Express listening on port ${port}`);
});
