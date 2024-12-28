# Use a lightweight base image tailored for the application type
FROM node:14-alpine

# Set the working directory
WORKDIR /app

# Copy the package.json file
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the application code
COPY . .

# Expose the container port
EXPOSE 80

# Run the command to start the application
CMD ["npm", "start"]
