import express from "express";
import * as identityController from "../controllers/identityController.js";
import jwtMiddleware from "../middleware/middleware.js";

const identityRouter = express.Router();

/**
 * @swagger
 * components:
 *   schemas:
 *     IdentityProfile:
 *       type: object
 *       required:
 *         - student_id
 *         - name
 *         - description
 *         - did
 *         - verifiable_credential
 *       properties:
 *         _id:
 *           type: string
 *           description: The auto-generated id of the identity profile
 *         student_id:
 *           type: string
 *           description: Unique student identification
 *         name:
 *           type: string
 *           description: Student name
 *         description:
 *           type: string
 *           description: Profile description
 *         image:
 *           type: string
 *           description: Profile image URL
 *         method:
 *           type: string
 *           enum: [did, web3]
 *           default: did
 *           description: Identity verification method
 *         did:
 *           type: string
 *           description: Decentralized Identifier
 *         verifiable_credential:
 *           type: string
 *           description: Verifiable credential data
 *         created_at:
 *           type: string
 *           format: date-time
 *           description: Creation timestamp
 *         updated_at:
 *           type: string
 *           format: date-time
 *           description: Last update timestamp
 *     CreateIdentityProfileRequest:
 *       type: object
 *       required:
 *         - student_id
 *         - name
 *         - description
 *         - did
 *         - verifiable_credential
 *       properties:
 *         student_id:
 *           type: string
 *           example: "ST001"
 *         name:
 *           type: string
 *           example: "Nguyen Van A"
 *         description:
 *           type: string
 *           example: "Computer Science Student"
 *         image:
 *           type: string
 *           example: "https://example.com/avatar.jpg"
 *         method:
 *           type: string
 *           enum: [did, web3]
 *           default: did
 *         did:
 *           type: string
 *           example: "did:key:z6LSe8eJ4CWfNAqFLQVW44sMcpsZ5eTNorDESTy3ToGAr1ZS"
 *         verifiable_credential:
 *           type: string
 *           example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
 */

/**
 * @swagger
 * /api/v1/identity/create:
 *   post:
 *     summary: Create a new identity profile
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/CreateIdentityProfileRequest'
 *     responses:
 *       201:
 *         description: Identity profile created successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   $ref: '#/components/schemas/IdentityProfile'
 *       400:
 *         description: Bad request or student ID already exists
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.post("/create", jwtMiddleware, identityController.createIdentityProfile);

/**
 * @swagger
 * /api/v1/identity/all:
 *   get:
 *     summary: Get all identity profiles
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Identity profiles retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/IdentityProfile'
 *                 count:
 *                   type: number
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.get("/all", jwtMiddleware, identityController.getAllIdentityProfiles);

/**
 * @swagger
 * /api/v1/identity/{id}:
 *   get:
 *     summary: Get identity profile by ID
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: Identity profile ID
 *     responses:
 *       200:
 *         description: Identity profile retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   $ref: '#/components/schemas/IdentityProfile'
 *       404:
 *         description: Identity profile not found
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.get("/:id", jwtMiddleware, identityController.getIdentityProfileById);

/**
 * @swagger
 * /api/v1/identity/student/{student_id}:
 *   get:
 *     summary: Get identity profile by student ID
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: student_id
 *         schema:
 *           type: string
 *         required: true
 *         description: Student ID
 *     responses:
 *       200:
 *         description: Identity profile retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   $ref: '#/components/schemas/IdentityProfile'
 *       404:
 *         description: Identity profile not found
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.get("/student/:student_id", jwtMiddleware, identityController.getIdentityProfileByStudentId);

/**
 * @swagger
 * /api/v1/identity/{id}:
 *   put:
 *     summary: Update identity profile
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: Identity profile ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               student_id:
 *                 type: string
 *               name:
 *                 type: string
 *               description:
 *                 type: string
 *               image:
 *                 type: string
 *               method:
 *                 type: string
 *                 enum: [did, web3]
 *               did:
 *                 type: string
 *               verifiable_credential:
 *                 type: string
 *     responses:
 *       200:
 *         description: Identity profile updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   $ref: '#/components/schemas/IdentityProfile'
 *       400:
 *         description: Bad request or duplicate student ID
 *       404:
 *         description: Identity profile not found
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.put("/update/:id", jwtMiddleware, identityController.updateIdentityProfile);

/**
 * @swagger
 * /api/v1/identity/{id}:
 *   delete:
 *     summary: Delete identity profile
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: Identity profile ID
 *     responses:
 *       200:
 *         description: Identity profile deleted successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   $ref: '#/components/schemas/IdentityProfile'
 *       404:
 *         description: Identity profile not found
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.delete("/:id", jwtMiddleware, identityController.deleteIdentityProfile);

/**
 * @swagger
 * /api/v1/identity/method/{method}:
 *   get:
 *     summary: Get identity profiles by method
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: method
 *         schema:
 *           type: string
 *           enum: [did, web3]
 *         required: true
 *         description: Identity verification method
 *     responses:
 *       200:
 *         description: Identity profiles retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/IdentityProfile'
 *                 count:
 *                   type: number
 *       400:
 *         description: Invalid method
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.get("/method/:method", jwtMiddleware, identityController.getIdentityProfilesByMethod);

/**
 * @swagger
 * /api/v1/identity/search:
 *   get:
 *     summary: Search identity profiles
 *     tags: [Identity Profile]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: q
 *         schema:
 *           type: string
 *         description: Search query (searches in name, description, student_id)
 *       - in: query
 *         name: method
 *         schema:
 *           type: string
 *           enum: [did, web3]
 *         description: Filter by identity verification method
 *     responses:
 *       200:
 *         description: Search completed successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 status:
 *                   type: boolean
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/IdentityProfile'
 *                 count:
 *                   type: number
 *                 query:
 *                   type: object
 *                   properties:
 *                     q:
 *                       type: string
 *                     method:
 *                       type: string
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
identityRouter.get("/search", jwtMiddleware, identityController.searchIdentityProfiles);

export default identityRouter;
