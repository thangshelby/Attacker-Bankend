import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import path from "path";
import { fileURLToPath } from "url";
import { EventEmitter } from "events";

// Increase the default max listeners to prevent warning
EventEmitter.defaultMaxListeners = 15;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROTO_PATH = path.join(__dirname, "../base.proto");

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

const client = new protoDescriptor.base.BaseService(
  "localhost:50051",
  grpc.credentials.createInsecure()
);

export default client;
