import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as apigatewayv2 from '@aws-cdk/aws-apigatewayv2-alpha';
import * as apigatewayv2_integrations from '@aws-cdk/aws-apigatewayv2-integrations-alpha';
import { Construct } from 'constructs';

export class ApiStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create S3 buckets first
        const staticBucket = new s3.Bucket(this, 'StaticBucket', {
            bucketName: `essay-checker-static-${this.account}`,
            removalPolicy: cdk.RemovalPolicy.RETAIN,
        });

        const storageBucket = new s3.Bucket(this, 'StorageBucket', {
            bucketName: `essay-checker-storage-${this.account}`,
            removalPolicy: cdk.RemovalPolicy.RETAIN,
        });

        // Create SQS queue
        const queue = new sqs.Queue(this, 'TaskQueue', {
            queueName: 'essay-checker-task-queue',
        });

        // Create Docker image asset
        const dockerImage = new ecr_assets.DockerImageAsset(this, 'ApiImage', {
            directory: path.join(__dirname, '../..'),
            file: 'Dockerfile',
            exclude: [
                'infrastructure/cdk.out',
                'infrastructure/node_modules',
                '**/__pycache__',
                '**/venv',
                '.git',
            ],
        });

        // Create Lambda function
        const handler = new lambda.DockerImageFunction(this, 'ApiHandler', {
            code: lambda.DockerImageCode.fromEcr(dockerImage.repository, {
                tagOrDigest: dockerImage.imageTag,
            }),
            memorySize: 1024,
            timeout: cdk.Duration.seconds(30),
            environment: {
                LAMBDA_AWS_REGION: this.region,
                S3_AWS_STATIC_BUCKET_NAME: staticBucket.bucketName,
                S3_AWS_STORAGE_BUCKET_NAME: storageBucket.bucketName,
                SQS_AWS_QUEUE_URL: queue.queueUrl,
                USE_LOCALSTACK: 'False',
                AWS_LAMBDA_EXEC_WRAPPER: '/opt/extensions/lambda-adapter',
                PORT: '8080',
            },
            logRetention: cdk.aws_logs.RetentionDays.ONE_WEEK,
            initialPolicy: [
                new cdk.aws_iam.PolicyStatement({
                    effect: cdk.aws_iam.Effect.ALLOW,
                    actions: [
                        'logs:CreateLogGroup',
                        'logs:CreateLogStream',
                        'logs:PutLogEvents'
                    ],
                    resources: ['*']
                })
            ]
        });

        // After creating the Lambda but before creating the API Gateway
        handler.addPermission('ApiGatewayInvoke', {
            principal: new cdk.aws_iam.ServicePrincipal('apigateway.amazonaws.com'),
            action: 'lambda:InvokeFunction',
            sourceArn: `arn:aws:execute-api:${this.region}:${this.account}:*/*/*/*`
        });

        // Create API Gateway with logging enabled
        const api = new apigatewayv2.HttpApi(this, 'ApiGateway', {
            description: 'Essay Checker API',
            corsPreflight: {
                allowMethods: [apigatewayv2.CorsHttpMethod.ANY],
                allowOrigins: ['*'],
                allowHeaders: ['*']
            }
        });

        // Add the Lambda integration
        api.addRoutes({
            path: '/{proxy+}',
            methods: [apigatewayv2.HttpMethod.ANY],
            integration: new apigatewayv2_integrations.HttpLambdaIntegration(
                'LambdaIntegration',
                handler
            )
        });

        // Grant permissions
        staticBucket.grantReadWrite(handler);
        storageBucket.grantReadWrite(handler);
        queue.grant(handler,
            'sqs:ChangeMessageVisibility',
            'sqs:DeleteMessage',
            'sqs:GetQueueAttributes',
            'sqs:GetQueueUrl',
            'sqs:ReceiveMessage',
            'sqs:SendMessage'
        );

        // Output the API URL
        new cdk.CfnOutput(this, 'ApiUrl', {
            value: api.apiEndpoint,
        });

        // Output other resource names/URLs
        new cdk.CfnOutput(this, 'StaticBucketName', {
            value: staticBucket.bucketName,
        });

        new cdk.CfnOutput(this, 'StorageBucketName', {
            value: storageBucket.bucketName,
        });

        new cdk.CfnOutput(this, 'QueueUrl', {
            value: queue.queueUrl,
        });
    }
} 