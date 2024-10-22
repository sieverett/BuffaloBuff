## BuffaloBuffBot – Telegram Chatbot with Azure OpenAI Integration


<img src="imgs/buffalo.png" alt="Description" width="400" height="400">


##
Welcome to the **BuffaloBuffBot** project! This repository contains the code for a Telegram chatbot integrated with Azure OpenAI, providing mechanical support for World Bicycle Relief's Buffalo Bikes. This guide will walk you through the steps to run this bot locally in Docker, deploy it on Azure, and set up CI/CD pipelines via GitHub Actions.

### Prerequisites

Before proceeding, ensure you have the following prerequisites installed:

- **Docker**: For running the bot locally in a container.
- **Azure Account**: You'll need an Azure subscription to deploy the bot.
- **Azure CLI**: To interact with Azure from the command line.
- **GitHub Account**: For version control and setting up CI/CD pipelines.
- **Telegram Bot Token**: Create a bot via the [Telegram BotFather](https://core.telegram.org/bots#botfather) to get your bot token.
- **OpenAI API Key**: Register with Azure OpenAI to get the necessary API key.

### Local Setup (Docker)

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/buffalobuffbot.git
   cd buffalobuffbot
   ```

2. **Create an `.env` file**:

   Inside the project directory, create an `.env` file with the following content:

   ```bash
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   AZURE_OPENAI_API_KEY=your-azure-openai-api-key
   AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint
   DEPLOYMENT_NAME=your-openai-deployment-name
   ```

   Replace `your-telegram-bot-token`, `your-azure-openai-api-key`, etc., with your actual values.

3. **Build and run the Docker container**:

   ```bash
   docker build -t buffalobuffbot .
   docker run -p 8000:8000 --env-file .env buffalobuffbot
   ```

   This will start the bot locally. You can test it by messaging the bot on Telegram.

### Deploy to Azure

#### Step 1: Set Up Azure Resources

1. **Log in to Azure**:

   ```bash
   az login
   ```

2. **Create a resource group**:

   ```bash
   az group create --name buffaloBotResourceGroup --location eastus
   ```

3. **Create Azure App Service**:

   ```bash
   az appservice plan create --name buffaloBuffBotPlan --resource-group buffaloBotResourceGroup --sku B1 --is-linux
   ```

4. **Create a web app**:

   ```bash
   az webapp create --resource-group buffaloBotResourceGroup --plan buffaloBuffBotPlan --name buffaloBuffBot --deployment-container-image-name yourdockerhubusername/buffalobuffbot:latest
   ```

5. **Set environment variables in Azure**:

   ```bash
   az webapp config appsettings set --name buffaloBuffBot --resource-group buffaloBotResourceGroup --settings TELEGRAM_BOT_TOKEN=your-telegram-bot-token AZURE_OPENAI_API_KEY=your-openai-api-key AZURE_OPENAI_ENDPOINT=your-azure-endpoint DEPLOYMENT_NAME=your-deployment-name
   ```

6. **Configure Docker for the web app**:

   ```bash
   az webapp config container set --name buffaloBuffBot --resource-group buffaloBotResourceGroup --docker-custom-image-name yourdockerhubusername/buffalobuffbot:latest
   ```

7. **Browse your app**:

   ```bash
   az webapp browse --name buffaloBuffBot --resource-group buffaloBotResourceGroup
   ```

Your bot should now be running on Azure and accessible via Telegram.

### CI/CD with GitHub Actions

To set up continuous integration and deployment (CI/CD) from GitHub to Azure:

1. **Create GitHub Secrets**:

   In your GitHub repository, navigate to **Settings > Secrets and variables > Actions** and add the following secrets:

   - **AZURE_CREDENTIALS**: This is the JSON output from the Service Principal you created earlier using:

     ```bash
     az ad sp create-for-rbac --name "buffaloBuffBotServicePrincipal" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} --sdk-auth
     ```

   - **AZURE_WEBAPP_NAME**: The name of your Azure App Service (e.g., `buffaloBuffBot`).
   - **AZURE_RESOURCE_GROUP**: The name of your Azure Resource Group (e.g., `buffaloBotResourceGroup`).
   - **AZURE_CONTAINER_REGISTRY**: The name of your Azure Container Registry.
   - **AZURE_REGISTRY_USERNAME** and **AZURE_REGISTRY_PASSWORD**: The `clientId` and `clientSecret` from the Service Principal.
   - **TELEGRAM_BOT_TOKEN**, **AZURE_OPENAI_API_KEY**, **AZURE_OPENAI_ENDPOINT**, **DEPLOYMENT_NAME**: These are the same values from your `.env` file.

2. **Add a GitHub Actions workflow file**:

   Create a `.github/workflows/azure-deployment.yml` file with the following content:

   ```yaml
   name: Deploy to Azure

   on:
     push:
       branches:
         - main

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
       - name: Checkout code
         uses: actions/checkout@v2

       - name: Log in to Azure
         uses: azure/login@v1
         with:
           creds: ${{ secrets.AZURE_CREDENTIALS }}

       - name: Build and push Docker image to ACR
         run: |
           docker build -t ${{ secrets.AZURE_CONTAINER_REGISTRY }}/buffalobuffbot .
           echo "${{ secrets.AZURE_REGISTRY_PASSWORD }}" | docker login ${{ secrets.AZURE_CONTAINER_REGISTRY }} -u ${{ secrets.AZURE_REGISTRY_USERNAME }} --password-stdin
           docker push ${{ secrets.AZURE_CONTAINER_REGISTRY }}/buffalobuffbot

       - name: Deploy to Azure Web App
         uses: azure/webapps-deploy@v2
         with:
           app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
           publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}

       - name: Set environment variables in Azure
         run: |
           az webapp config appsettings set --name ${{ secrets.AZURE_WEBAPP_NAME }} --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} --settings TELEGRAM_BOT_TOKEN=${{ secrets.TELEGRAM_BOT_TOKEN }} AZURE_OPENAI_API_KEY=${{ secrets.AZURE_OPENAI_API_KEY }} AZURE_OPENAI_ENDPOINT=${{ secrets.AZURE_OPENAI_ENDPOINT }} DEPLOYMENT_NAME=${{ secrets.DEPLOYMENT_NAME }}
   ```

3. **Push your code**:

   Push your changes to the `main` branch, and GitHub Actions will automatically build and deploy your app to Azure.

### Additional Considerations

- **Scaling**: If you expect heavy traffic, consider using **Azure Kubernetes Service (AKS)** for load balancing and auto-scaling. Azure App Service Plans like **Standard** or **Premium** also offer scaling features.
  
- **Logging**: Use **Azure Monitor** to track logs and performance. You can also access logs via the **App Service > Log Stream** in the Azure portal.

### Conclusion

You’ve now set up the BuffaloBuffBot on your local machine, deployed it to Azure, and configured CI/CD with GitHub Actions. This bot can be further enhanced with caching, scaling, and monitoring as your usage grows.

Feel free to reach out if you have any questions or suggestions!

### License
This project is licensed under the MIT License.

