# Use Node.js 20 or higher
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose the development port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]