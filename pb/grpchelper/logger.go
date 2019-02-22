package grpchelper

import (
	"context"
	"path"
	"time"

	"google.golang.org/grpc"
	"gopkg.in/src-d/lookout-sdk.v0/pb"
)

// LogFn is the function used to log the messages
type LogFn func(msg string, fields pb.Fields)

// LogUnaryServerInterceptor returns a new unary server interceptor that logs
// request/response.
func LogUnaryServerInterceptor(log LogFn) grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		startTime := time.Now()

		logCtx := buildServerRequestCtx(ctx, info.FullMethod)
		log("gRPC unary server call started", pb.GetLogFields(logCtx))

		resp, err := handler(ctx, req)

		logCtx = buildResponseLoggerCtx(logCtx, startTime, err)
		log("gRPC unary server call finished", pb.GetLogFields(logCtx))

		return resp, err
	}
}

// LogStreamServerInterceptor returns a new streaming server interceptor that
// logs request/response.
func LogStreamServerInterceptor(log LogFn) grpc.StreamServerInterceptor {
	return func(srv interface{}, stream grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) error {
		startTime := time.Now()

		logCtx := buildServerRequestCtx(stream.Context(), info.FullMethod)
		log("gRPC streaming server call started", pb.GetLogFields(logCtx))

		err := handler(srv, stream)

		logCtx = buildResponseLoggerCtx(logCtx, startTime, err)
		log("gRPC streaming server call finished", pb.GetLogFields(logCtx))

		return err
	}
}

// LogUnaryClientInterceptor returns a new unary client interceptor that logs
// the execution of external gRPC calls.
func LogUnaryClientInterceptor(log LogFn) grpc.UnaryClientInterceptor {
	return func(ctx context.Context, method string, req, reply interface{}, cc *grpc.ClientConn, invoker grpc.UnaryInvoker, opts ...grpc.CallOption) error {
		startTime := time.Now()

		logCtx := buildClientRequestCtx(ctx, method)
		log("gRPC unary client call started", pb.GetLogFields(logCtx))

		err := invoker(ctx, method, req, reply, cc, opts...)

		logCtx = buildResponseLoggerCtx(logCtx, startTime, err)
		log("gRPC unary client call finished", pb.GetLogFields(logCtx))

		return err
	}
}

// LogStreamClientInterceptor returns a new streaming client interceptor that
// logs the execution of external gRPC calls.
func LogStreamClientInterceptor(log LogFn) grpc.StreamClientInterceptor {
	return func(ctx context.Context, desc *grpc.StreamDesc, cc *grpc.ClientConn, method string, streamer grpc.Streamer, opts ...grpc.CallOption) (grpc.ClientStream, error) {
		startTime := time.Now()

		logCtx := buildClientRequestCtx(ctx, method)
		log("gRPC streaming client call started", pb.GetLogFields(logCtx))

		clientStream, err := streamer(ctx, desc, cc, method, opts...)

		logCtx = buildResponseLoggerCtx(ctx, startTime, err)
		log("gRPC streaming client call finished", pb.GetLogFields(logCtx))

		return clientStream, err
	}
}

func buildServerRequestCtx(ctx context.Context, fullMethod string) context.Context {
	return buildRequestCtx(ctx, "server", fullMethod)
}

func buildClientRequestCtx(ctx context.Context, fullMethod string) context.Context {
	return buildRequestCtx(ctx, "client", fullMethod)
}

func buildRequestCtx(ctx context.Context, kind, fullMethod string) context.Context {
	service := path.Dir(fullMethod)[1:]
	method := path.Base(fullMethod)

	return pb.UpdateLogFields(ctx, pb.Fields{
		"system":       "grpc",
		"span.kind":    kind,
		"grpc.service": service,
		"grpc.method":  method,
	})
}

func buildResponseLoggerCtx(ctx context.Context, startTime time.Time, err error) context.Context {
	fields := pb.Fields{
		"grpc.start_time": startTime.Format(time.RFC3339),
		"grpc.code":       grpc.Code(err),
		"duration":        time.Now().Sub(startTime),
	}

	if err != nil {
		fields["error"] = err
	}

	return pb.UpdateLogFields(ctx, fields)
}
