#!/bin/bash
# Multi-Node Deployment Script for Jarvis V0.19
# Optimized for load balancing and high availability

set -e

# Configuration
JARVIS_DIR="/opt/jarvis"
NODE_COUNT=3
BASE_PORT=8000
LOG_DIR="/var/log/jarvis"

echo "Starting Jarvis V0.19 Multi-Node Deployment..."

# Create directories
sudo mkdir -p $JARVIS_DIR
sudo mkdir -p $LOG_DIR
sudo chown $USER:$USER $JARVIS_DIR $LOG_DIR

# Deploy application files
echo "Deploying application files..."
cp -r . $JARVIS_DIR/
cd $JARVIS_DIR

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start load balancer
echo "Starting load balancer..."
python deployment/load_balancing/multi_node_coordinator.py &
LB_PID=$!
echo $LB_PID > $LOG_DIR/loadbalancer.pid

# Start application nodes
echo "Starting $NODE_COUNT application nodes..."
for i in $(seq 1 $NODE_COUNT); do
    PORT=$((BASE_PORT + i))
    echo "Starting node $i on port $PORT..."
    
    # Start each node in background
    PORT=$PORT python main.py --node-id=node_$i > $LOG_DIR/node_$i.log 2>&1 &
    NODE_PID=$!
    echo $NODE_PID > $LOG_DIR/node_$i.pid
    
    echo "Node $i started with PID $NODE_PID"
done

# Health check
echo "Performing health checks..."
sleep 5

for i in $(seq 1 $NODE_COUNT); do
    PORT=$((BASE_PORT + i))
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "Node $i (port $PORT): ✅ Healthy"
    else
        echo "Node $i (port $PORT): ❌ Unhealthy"
    fi
done

echo "Multi-node deployment completed!"
echo "Load balancer PID: $LB_PID"
echo "Check logs in: $LOG_DIR"

# Create stop script
cat > $JARVIS_DIR/stop_deployment.sh << 'EOF'
#!/bin/bash
LOG_DIR="/var/log/jarvis"

echo "Stopping Jarvis V0.19 deployment..."

# Stop load balancer
if [ -f $LOG_DIR/loadbalancer.pid ]; then
    kill $(cat $LOG_DIR/loadbalancer.pid) 2>/dev/null || true
    rm $LOG_DIR/loadbalancer.pid
fi

# Stop all nodes
for pid_file in $LOG_DIR/node_*.pid; do
    if [ -f "$pid_file" ]; then
        kill $(cat "$pid_file") 2>/dev/null || true
        rm "$pid_file"
    fi
done

echo "Deployment stopped."
EOF

chmod +x $JARVIS_DIR/stop_deployment.sh
echo "Stop script created: $JARVIS_DIR/stop_deployment.sh"
