import matplotlib.pyplot as plt
import numpy as np
import wandb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from keras.datasets import fashion_mnist
import math

wandb.login(key = 'fc18454f0555cdcc5d98e84dfb27e127061d3d8b')

# Load MNIST data using Keras
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
x_train,x_val, y_train, y_val=train_test_split(x_train,y_train, test_size=0.2,shuffle=True,random_state=42)

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat','Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
wandb.init(project="Shubhodeep_Final_CS6190_DeepLearing_Assignment1",name = "Question 1")

# Create a figure to display the sample images
plt.figure(figsize=(10, 10))

# Plot one sample image for each class
for class_index in range(len(class_names)):
    # Find the index of the first image with the current class label
    sample_index = np.where(y_train == class_index)[0][0]
    
    # Get the image and its corresponding label
    image = x_train[sample_index]
    label = class_names[y_train[sample_index]]
    
    # Plot the image
    plt.subplot(2, 5, class_index + 1)
    plt.imshow(image, cmap=plt.cm.binary)
    plt.title(label)
    plt.axis('off')

# Log the figure to Wandb
wandb.log({"Question 1": wandb.Image(plt)})
plt.show()

#wandb.log({"Question 1": output_images})
wandb.finish()

# Preprocess the data
x_train = x_train/255.0 #.astype('float128') / 255.0
x_val = x_val/255 #astype('float128')/ 255.0

encoder = OneHotEncoder(sparse_output=False)

# Fit and transform the target values using OneHotEncoder
y_train = encoder.fit_transform(y_train.reshape(-1, 1))
print(y_train[0])
y_val = encoder.transform(y_val.reshape(-1, 1))
y_test = encoder.transform(y_test.reshape(-1, 1))

# Flatten the images
x_train = x_train.reshape((-1, 28 * 28))
print(x_train.shape)
x_val = x_val.reshape((-1, 28 * 28))
x_test = x_test.reshape((-1, 28 * 28))

class Activations :
    def sigmoid(self,x) :
        x = np.clip(x,-200,200)
        return 1/(1 + np.exp(-x))
    
    def g3(self,a):
        return np.maximum(a,0)

    def SoftMax(self,a):
        max_a = np.max(a)
        exp_a = np.exp(a - max_a)
        sum_exp_a = np.sum(exp_a)
        y = exp_a / sum_exp_a
        return y

class Differential :
    def sig_dif(self,a):
        activ = Activations()
        g_x = activ.sigmoid(a)
        return g_x*(1-g_x)

    def tan_dif(self,a):
        g_dash = np.tanh(a)
        return 1 - (g_dash**2)

    def Rel_dif(self,a):
        return (a > 0).astype('float64')

class Initializer :

    def Initialize(self,hidden_layers,npl):
        W = [[]]    # list consisting of all the W's

        # Create and append each Wi matrix filled with zeros to the list
        W.append(np.zeros((npl,784)))           #input layer h0 weight  : W1

        for _ in range(hidden_layers-1):
            W.append(np.zeros((npl,npl)))       #create the W for each hidden layer : [ W2 ... W(L-1) ]

        W.append(np.zeros((10,npl)))            #Weight for the final layer : WL

        b = [[]]    # list consiting of all the b's

        # Create and append each bi vector filled with zeros to the list
        b.append(np.zeros(npl))       #input layer h0 bias

        for _ in range(hidden_layers-1):
            b.append(np.zeros(npl))   #create the b for each hidden layer : [ b2 ... b(L-1) ]

        b.append(np.zeros(10))        #bias for the final layer : bL

        return W,b


    def Initialize2(self,hidden_layers,npl):
        W = [[]]    # list consisting of all the W's

        # Create and append each Wi matrix filled with random values to the list
        W.append(np.random.randn(npl, 784))         #input layer h0 weight  : W1
        for _ in range(hidden_layers-1):
            W.append(np.random.randn(npl, npl))     #create the W for each hidden layer : [ W2 ... W(L-1) ]

        W.append(np.random.randn(10, npl))      #Weight for the final layer : WL

        b = [[]]    # list consiting of all the b's

        # Create and append each bi vector filled with random values to the list
        b.append(np.random.randn(npl))          #input layer h0 bias

        for _ in range(hidden_layers-1):
            b.append(np.random.randn(npl))      #create the b for each hidden layer : [ b2 ... b(L-1) ]
                
        b.append(np.random.randn(10))       #bias for the final layer : bL
        return W,b

    def XavierIntializer(self,hidden_layers,npl):
        W = [[]]  # list consisting of all the W's

        # Xavier initialization for weights
        def xavier_init(n_in, n_out):
            return np.random.randn(n_out, n_in)* np.sqrt(1 / n_in)      

        # Create and append each Wi matrix filled with Xavier-initialized values to the list
        W.append(xavier_init(784, npl))  # input layer h0
        for _ in range(hidden_layers - 1):
            W.append(xavier_init(npl, npl))

        W.append(xavier_init(npl, 10))

        b = [[]]  # list consisting of all the b's

        # Xavier initialization for biases (can also be initialized with zeros)
        def bias_init(n_out):
            return np.zeros(n_out, dtype=np.float64)

        # Create and append each bi vector filled with Xavier-initialized values to the list
        b.append(bias_init(npl))
        for _ in range(hidden_layers - 1):
            b.append(bias_init(npl))

        b.append(bias_init(10))
        return W, b

class Arithmetic :
    def Add(self,u,v):          #Adds two matrices u,v of the same order
        for i in range(1,len(u)):
            u[i] = u[i] + v[i]
        return u

    def Subtract(self,v,dv,eta):    #Update rule : W(t+1) = W(t) + eta*delW
        for i in range(1,len(v)):
            v[i] = v[i] - (eta * dv[i])
        return v

    def RMSpropSubtract(self,v,dv,lv,eps,eta):     #Update rule : W(t+1) = W(t) + eta*delW
        for i in range(1,len(v)):
            ueta = eta/(np.sqrt(np.sum(lv[i])) + eps)
            v[i] = v[i] - (ueta * dv[i])
        return v

    def AdamSubtract(self,V,mV_hat,vV_hat,eps,eta):     #Update rule : W(t+1) = W(t) + eta*delW
        for i in range(1,len(V)):
            norm = np.linalg.norm(vV_hat[i])
            ueta = eta/(np.sqrt(norm) + eps)
            V[i] = V[i] - (ueta * mV_hat[i])
        return V


class Gradient_descent :
    def __init__(self, input_size, output_size, config):
        self.input_size = input_size
        self.output_size = output_size
        self.layers = config['layers']
        self.activation = config['activation']
        self.npl = config["neurons_per_layer"]
        self.eta = config["learning_rate"]
        self.batch = config["batch_size"]
        self.init = config["Initialization"]
        self.config = config

    def backward_propagation(self,A,H,W,b,y):
        L = self.layers

        delA = [[]]*(L+1)
        delW = [[]]*(L+1)
        delb = [[]]*(L+1)
        delh = [[]]*(L+1)
        
        delA[L] = -(y - H[L])

        for k in range(L,0,-1):
            delW[k] = np.matmul(delA[k],H[k-1].T) 
            delb[k] = np.sum(delA[k],axis = 1)
            delh[k-1] = W[k].T @ delA[k]
            if k>1 :
                diff_vect = np.array(A[k-1])
                d = Differential()
                if self.activation == 'sigmoid':
                    diff_vect = d.sig_dif(A[k-1])
                elif self.activation == 'tanh':
                    diff_vect = d.tan_dif(A[k-1])
                else :
                    diff_vect = d.Rel_dif(A[k-1])
                delA[k-1] = np.multiply(delh[k-1],diff_vect)

        return delW,delb

    def forward_propagation(self,W,b,layers,inpl):
        A = [[]]
        H = [inpl]
        
        activ = Activations()
        
        for i in range (1,layers) :
            rep = (H[i-1].shape[1],1)
            bias = np.tile(b[i],rep).transpose()
            
            a = np.add(bias,np.dot(W[i],H[i-1]))

            A.append(a)
            h = a

            if self.activation == 'sigmoid':   # Sigmoid activation function
                h = activ.sigmoid(a)
            elif self.activation == 'tanh':   # tanh activation function
                h = np.tanh(a)
            else :            # ReLU activation function
                h = activ.g3(a)

            H.append(h)
        
        bias_new = b[layers]
        bias_new = np.tile(bias_new[:, np.newaxis], (1, self.batch))
        a = np.add(bias_new,np.inner(W[layers],H[layers-1].T))
      
        A.append(a)
        a_trans = a.T
        y_hat = []
        for i in range(len(a_trans)):
            y_hat.append(activ.SoftMax(a_trans[i]))
        y_hat = np.array(y_hat)
        y_hat = y_hat.T
        H.append(y_hat)
        return A,H
    
    def calc_val_loss(self,W,b):
        s = 0.0
        c = 0
        for j in range(0,len(x_val)//self.batch):
                
            h0 = x_val[j*self.batch : (j+1)*self.batch]
                
            A,H = self.forward_propagation(W,b,self.layers,h0.T)
                
            y = y_val[j*self.batch : (j+1)*self.batch]
                
            yp = H[self.layers].T
            for itr in range(self.batch):
                if self.config['loss'] == 'cross_entropy' :
                    s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                else :
                    s = s + np.sum((y[itr]-yp[itr])**2)
                if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                    c = c + 1
        return [s,c]
            
    def Stocastic_Gradient_descent(self) :
        epochs = self.config['epochs']
        W = []    # list consisting of all the W's
        b = []    # list consiting of all the b's
        
        I = Initializer()
        if(self.init == "random"):
            W,b = I.Initialize2(self.layers-1,self.npl)
        else:
            W,b = I.XavierIntializer(self.layers-1,self.npl)
        
        training_loss = []
        validation_loss = []
        training_accuracy = []
        validation_accuracy = []
        for i in range(epochs):
            s = 0.0
            c = 0
            for j in range(0,len(x_train)//self.batch):
                
                h0 = x_train[j*self.batch : (j+1)*self.batch]
                
                A,H = self.forward_propagation(W,b,self.layers,h0.T)
                
                y = y_train[j*self.batch : (j+1)*self.batch]
                
                yp = H[self.layers].T
                for itr in range(self.batch):
                    if self.config['loss'] == 'cross_entropy' :
                        s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                    else :
                        s = s + np.sum((y[itr]-yp[itr])**2)
                    if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                        c = c + 1

                delW,delb = self.backward_propagation(A,H,W,b,y.T)
                PMA = Arithmetic()    # P - Plus, M - Minus , A - Arithmetic
                W = PMA.Subtract(W,delW,self.eta)
                W = PMA.Subtract(W,W,self.eta*self.config['regularization'])
                b = PMA.Subtract(b,delb,self.eta)
            
            training_loss.append(s/len(x_train))
            training_accuracy.append(c*100/len(x_train))
            vl = self.calc_val_loss(W,b)
            validation_loss.append(vl[0]/len(x_val))
            validation_accuracy.append(vl[1]*100/len(x_val))
            wandb.log({"training_loss": training_loss[-1],"validation_loss": validation_loss[-1],"training_accuracy":training_accuracy[-1],"validation_accuracy":validation_accuracy[-1],'epoch':i+1})
            print('******************************************************************************************')
            print('epoch : ',i+1)
            print('Training accuracy :',training_accuracy[-1],'Training Loss :',training_loss[-1]) 
            print('Validation accuracy :',validation_accuracy[-1],'Validation Loss :',validation_loss[-1])
            print('******************************************************************************************')
         
        return W,b
    
    
    def Momentum_Gradient_descent(self) :
        epochs = self.config['epochs']
        W = []    # list consisting of all the W's
        b = []    # list consiting of all the b's

        I = Initializer()
        if(self.init == "random"):
            W,b = I.Initialize2(self.layers-1,self.npl)
        else:
            W,b = W,b = I.XavierIntializer(self.layers-1,self.npl)

        prev_uW,prev_ub = I.Initialize(self.layers-1,self.npl)
        beta = self.config['beta']
        
        training_loss = []
        validation_loss = []
        training_accuracy = []
        validation_accuracy = []

        for i in range(epochs):
            s = 0.0
            c = 0
            for j in range(0,len(x_train)//self.batch):
                
                h0 = x_train[j*self.batch : (j+1)*self.batch]
                
                A,H = self.forward_propagation(W,b,self.layers,h0.T)
                
                y = y_train[j*self.batch : (j+1)*self.batch]
                
                yp = H[self.layers].T
                for itr in range(self.batch):
                    if self.config['loss'] == 'cross_entropy' :
                        s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                    else :
                        s = s + np.sum((y[itr]-yp[itr])**2)
                    if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                        c = c + 1
            
                delW,delb = self.backward_propagation(A,H,W,b,y.T)
                PMA = Arithmetic()
                
                for k in range(1,len(prev_uW)):
                    prev_uW[k] = np.add(beta*prev_uW[k],delW[k])
                    prev_ub[k] = np.add(beta*prev_ub[k],delb[k])

                W = PMA.Subtract(W,prev_uW,self.eta)
                W = PMA.Subtract(W,W,self.eta*self.config['regularization'])
                b = PMA.Subtract(b,prev_ub,self.eta)
                
                    
            training_loss.append(s/len(x_train))
            training_accuracy.append(c*100/len(x_train))
            vl = self.calc_val_loss(W,b)
            validation_loss.append(vl[0]/len(x_val))
            validation_accuracy.append(vl[1]*100/len(x_val))
            wandb.log({"training_loss": training_loss[-1],"validation_loss": validation_loss[-1],"training_accuracy":training_accuracy[-1],"validation_accuracy":validation_accuracy[-1],'epoch':i+1})
            print('******************************************************************************************')
            print('epoch : ',i+1)
            print('Training accuracy :',training_accuracy[-1],'Training Loss :',training_loss[-1]) 
            print('Validation accuracy :',validation_accuracy[-1],'Validation Loss :',validation_loss[-1])
            print('******************************************************************************************')

        return W,b

    def NAG_descent(self) :    # function(layers ,neurons per layer)
        epochs =  self.config['epochs']
        W = []    # list consisting of all the W's
        b = []    # list consiting of all the b's

        I = Initializer()
        if(self.init == "random"):
            W,b = I.Initialize2(self.layers-1,self.npl)
            print(len(W),len(b))
        else:
            W,b = W,b = I.XavierIntializer(self.layers-1,self.npl)
        
        prev_vW,prev_vb = I.Initialize(self.layers-1,self.npl)
        beta = self.config['beta']
        
        training_loss = []
        validation_loss = []
        training_accuracy = []
        validation_accuracy = []
        
        for i in range(epochs):
            vW,vb = I.Initialize(self.layers-1,self.npl)
            for k in range(1,len(prev_vW)):
                vW[k] = beta*prev_vW[k]
                vb[k] = beta*prev_vb[k]
            s = 0.0
            c = 0
            
            ASA = Arithmetic()
            tempW = ASA.Subtract(W,vW,beta)
            tempb = ASA.Subtract(b,vb,beta)
            
            for j in range(0,len(x_train)//self.batch):
                
                h0 = x_train[j*self.batch : (j+1)*self.batch]
                
                A,H = self.forward_propagation(tempW,tempb,self.layers,h0.T)
                
                y = y_train[j*self.batch : (j+1)*self.batch]
                
                yp = H[self.layers].T
                for itr in range(self.batch):
                    if self.config['loss'] == 'cross_entropy' :
                        s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                    else :
                        s = s + np.sum((y[itr]-yp[itr])**2)
                    if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                        c = c + 1
            
                delW,delb = self.backward_propagation(A,H,tempW,tempb,y.T)

                for k in range(1,len(prev_vW)):
                    prev_vW[k] = beta*prev_vW[k] + self.eta*delW[k]
                    prev_vb[k] = beta*prev_vb[k] + self.eta*delb[k]

                W = ASA.Subtract(W,vW,1)
                W = ASA.Subtract(W,W,self.eta*self.config['regularization'])
                b = ASA.Subtract(b,vb,1)
                prev_vb = vb
                prev_vW = vW
                
            training_loss.append(s/len(x_train))
            training_accuracy.append(c*100/len(x_train))
            vl = self.calc_val_loss(W,b)
            validation_loss.append(vl[0]/len(x_val))
            validation_accuracy.append(vl[1]*100/len(x_val))
            wandb.log({"training_loss": training_loss[-1],"validation_loss": validation_loss[-1],"training_accuracy":training_accuracy[-1],"validation_accuracy":validation_accuracy[-1],'epoch':i+1})
            print('******************************************************************************************')
            print('epoch : ',i+1)
            print('Training accuracy :',training_accuracy[-1],'Training Loss :',training_loss[-1]) 
            print('Validation accuracy :',validation_accuracy[-1],'Validation Loss :',validation_loss[-1])
            print('******************************************************************************************')

        return W,b

    def RMSprop(self) :
        epochs = self.config["epochs"]

        I = Initializer()
        if(self.init == "random"):
            W,b = I.Initialize2(self.layers-1,self.npl)
        else:
            W,b = W,b = I.XavierIntializer(self.layers-1,self.npl)

        vW,vb = I.Initialize(self.layers-1,self.npl)
        beta = self.config['beta']
        eps = 1e-4
        
        training_loss = []
        validation_loss = []
        training_accuracy = []
        validation_accuracy = []
        
        for i in range(epochs):
            s = 0.0
            c = 0
            for j in range(0,len(x_train)//self.batch):
                h0 = x_train[j*self.batch : (j+1)*self.batch]
                
                A,H = self.forward_propagation(W,b,self.layers,h0.T)
                
                y = y_train[j*self.batch : (j+1)*self.batch]
                
                yp = H[self.layers].T
                for itr in range(self.batch):
                    if self.config['loss'] == 'cross_entropy' :
                        s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                    else :
                        s = s + np.sum((y[itr]-yp[itr])**2)
                    if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                        c = c + 1
            
                delW,delb = self.backward_propagation(A,H,W,b,y.T)
                PMA = Arithmetic()
               
                for k in range(1,len(vW)):
                    vW[k] = (beta * vW[k])+ ((1-beta)*(delW[k]**2))
                    vb[k] = (beta * vb[k])+ ((1-beta)*(delb[k]**2))

                W = PMA.RMSpropSubtract(W,delW,vW,eps,self.eta)
                W = PMA.Subtract(W,W,self.eta*self.config['regularization'])
                b = PMA.RMSpropSubtract(b,delb,vb,eps,self.eta)
                delW,delb = I.Initialize(self.layers-1,self.npl)
            
            training_loss.append(s/len(x_train))
            training_accuracy.append(c*100/len(x_train))
            vl = self.calc_val_loss(W,b)
            validation_loss.append(vl[0]/len(x_val))
            validation_accuracy.append(vl[1]*100/len(x_val))
            wandb.log({"training_loss": training_loss[-1],"validation_loss": validation_loss[-1],"training_accuracy":training_accuracy[-1],"validation_accuracy":validation_accuracy[-1],'epoch':i+1})
            print('******************************************************************************************')
            print('epoch : ',i+1)
            print('Training accuracy :',training_accuracy[-1],'Training Loss :',training_loss[-1]) 
            print('Validation accuracy :',validation_accuracy[-1],'Validation Loss :',validation_loss[-1])
            print('******************************************************************************************')

        return W,b

    def Adam(self) :
        epochs = self.config["epochs"]

        I = Initializer()
        if(self.init == "random"):
            W,b = I.Initialize2(self.layers-1,self.npl)
        else:
            W,b = W,b = I.XavierIntializer(self.layers-1,self.npl)

        training_loss = []
        validation_loss = []
        training_accuracy = []
        validation_accuracy = []
        
        vW,vb = I.Initialize(self.layers-1,self.npl)
        mW,mb = I.Initialize(self.layers-1,self.npl)
        beta1,beta2 = self.config['beta1'],self.config['beta2']

        for i in range(epochs):
            eps = 1e-10
            s = 0.0
            c = 0
            for j in range(0,len(x_train)//self.batch): 
                h0 = x_train[j*self.batch : (j+1)*self.batch]
                
                A,H = self.forward_propagation(W,b,self.layers,h0.T)
                
                y = y_train[j*self.batch : (j+1)*self.batch]
                
                yp = H[self.layers].T
                for itr in range(self.batch):
                    if self.config['loss'] == 'cross_entropy' :
                        s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                    else :
                        s = s + np.sum((y[itr]-yp[itr])**2)
                    if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                        c = c + 1
            
                delW,delb = self.backward_propagation(A,H,W,b,y.T)
                PMA = Arithmetic()

                vW_hat,vb_hat = I.Initialize(self.layers-1,self.npl)
                mW_hat,mb_hat = I.Initialize(self.layers-1,self.npl)

                for k in range(1,len(vW)):
                    mW[k] = (beta1 * mW[k]) + ((1-beta1)*(delW[k]))

                    mW_hat[k] = mW[k]/(1-np.power(beta1,i+1))
                    
                    mb[k] = (beta1 * mb[k]) + ((1-beta1)*(delb[k]))

                    mb_hat[k] = mb[k]/(1-np.power(beta1,i+1))

                    vW[k] = (beta2 * vW[k])+ ((1-beta2)*(delW[k]**2))

                    vW_hat[k] = vW[k]/(1-np.power(beta2,i+1))

                    vb[k] = (beta2 * vb[k])+ ((1-beta2)*(delb[k]**2))

                    vb_hat[k] = vb[k]/(1-np.power(beta2,i+1))
                    
                W = PMA.AdamSubtract(W,mW_hat,vW_hat,eps,self.eta)
                W = PMA.Subtract(W,W,self.eta*self.config['regularization'])
                b = PMA.AdamSubtract(b,mb_hat,vb_hat,eps,self.eta)
            
            training_loss.append(s/len(x_train))
            training_accuracy.append(c*100/len(x_train))
            vl = self.calc_val_loss(W,b)
            validation_loss.append(vl[0]/len(x_val))
            validation_accuracy.append(vl[1]*100/len(x_val))
            wandb.log({"training_loss": training_loss[-1],"validation_loss": validation_loss[-1],"training_accuracy":training_accuracy[-1],"validation_accuracy":validation_accuracy[-1],'epoch':i+1})
            print('******************************************************************************************')
            print('epoch : ',i+1)
            print('Training accuracy :',training_accuracy[-1],'Training Loss :',training_loss[-1]) 
            print('Validation accuracy :',validation_accuracy[-1],'Validation Loss :',validation_loss[-1])
            print('******************************************************************************************')

        return W,b

    def NAdam(self) :
        epochs = self.config["epochs"]

        I = Initializer()
        if(self.init == "random"):
            W,b = I.Initialize2(self.layers-1,self.npl)
        else:
            W,b = W,b = I.XavierIntializer(self.layers-1,self.npl)

        vW,vb = I.Initialize(self.layers-1,self.npl)
        mW,mb = I.Initialize(self.layers-1,self.npl)
        beta1,beta2 = self.config['beta1'],self.config['beta2']
        
        training_loss = []
        validation_loss = []
        training_accuracy = []
        validation_accuracy = []
        
        for i in range(epochs):
            eps = 1e-10
            s = 0.0
            c = 0
            for j in range(0,len(x_train)//self.batch): 
                h0 = x_train[j*self.batch : (j+1)*self.batch]
                
                A,H = self.forward_propagation(W,b,self.layers,h0.T)
                
                y = y_train[j*self.batch : (j+1)*self.batch]
                
                yp = H[self.layers].T
                for itr in range(self.batch):
                    if self.config['loss'] == 'cross_entropy' :
                        s = s - math.log(y[itr] @ yp[itr] + 1e-20)
                    else :
                        s = s + np.sum((y[itr]-yp[itr])**2)
                    if np.argmax(y[itr]) == np.argmax(yp[itr]) :
                        c = c + 1
            
                delW,delb = self.backward_propagation(A,H,W,b,y.T)
                PMA = Arithmetic()

                vW_hat,vb_hat = I.Initialize(self.layers-1,self.npl)
                mW_hat,mb_hat = I.Initialize(self.layers-1,self.npl)
                uW_hat,ub_hat = I.Initialize(self.layers-1,self.npl)
                for k in range(1,len(vW)):
                    mW[k] = (beta1 * mW[k]) + ((1-beta1)*(delW[k]))

                    mW_hat[k] = mW[k]/(1-np.power(beta1,i+1))

                    mb[k] = (beta1 * mb[k]) + ((1-beta1)*(delb[k]))

                    mb_hat[k] = mb[k]/(1-np.power(beta1,i+1))

                    vW[k] = (beta2 * vW[k])+ ((1-beta2)*(delW[k]**2))

                    vW_hat[k] = vW[k]/(1-np.power(beta2,i+1))

                    vb[k] = (beta2 * vb[k])+ ((1-beta2)*(delb[k]**2))

                    vb_hat[k] = vb[k]/(1-np.power(beta2,i+1))

                    uW_hat[k] = (beta1*mW_hat[k]) + (((1-beta1)/(1-(beta1)**(i+1)))*delW[k])

                    ub_hat[k] = (beta1*mb_hat[k]) + (((1-beta1)/(1-(beta1)**(i+1)))*delb[k])

                W = PMA.AdamSubtract(W,uW_hat,vW_hat,eps,self.eta)
                W = PMA.Subtract(W,W,self.eta*self.config['regularization'])
                b = PMA.AdamSubtract(b,ub_hat,vb_hat,eps,self.eta)
    
            training_loss.append(s/len(x_train))
            training_accuracy.append(c*100/len(x_train))
            vl = self.calc_val_loss(W,b)
            validation_loss.append(vl[0]/len(x_val))
            validation_accuracy.append(vl[1]*100/len(x_val))
            wandb.log({"training_loss": training_loss[-1],"validation_loss": validation_loss[-1],"training_accuracy":training_accuracy[-1],"validation_accuracy":validation_accuracy[-1],'epoch':i+1})
            print('******************************************************************************************')
            print('epoch : ',i+1)
            print('Training accuracy :',training_accuracy[-1],'Training Loss :',training_loss[-1]) 
            print('Validation accuracy :',validation_accuracy[-1],'Validation Loss :',validation_loss[-1])
            print('******************************************************************************************')

        return W,b
    
    def Run_Models(self):
        run_name = "op_{}_ep_{}_lay_{}_npl_{}_eta_{}_bs_{}_ini_{}_reg_{}_loss_{}_activ_{}".format(self.config['optimizer'],self.config['epochs'],self.config['layers'],self.config['neurons_per_layer'],self.config['learning_rate'],self.config['batch_size'],self.config['Initialization'],self.config['regularization'],self.config['loss'],self.config['activation'])
        wandb.run.name = run_name
        
        W,b = [],[]
        if self.config['optimizer'] == 'sgd' :
            W,b = self.Stocastic_Gradient_descent()
        elif self.config['optimizer'] == 'momentum' :
            W,b = self.Momentum_Gradient_descent()
        elif self.config['optimizer'] == 'nag' :
            W,b = self.NAG_descent()
        elif self.config['optimizer'] == 'rmsprop' :
            W,b = self.RMSprop()
        elif self.config['optimizer'] == 'adam' :
            W,b = self.Adam()
        else:
            W,b = self.NAdam()
        return W,b
        
def main():
    wandb.init(project="Shubhodeep_Final_CS6190_DeepLearing_Assignment1")
    config = wandb.config
    
    Model = Gradient_descent(784,10,config)
    W,b = Model.Run_Models()

sweep_config = {
    'method': 'bayes',
    'name' : 'sweep cross entropy',
    'metric': {
      'name': 'validation_accuracy',
      'goal': 'maximize'
    },
    'parameters': {
        'optimizer' : {'values' : ['sgd','momentum','nag','rmsprop','adam','nadam']},
        'epochs': {'values': [5,10,15,20]},
        'activation': {'values': ['sigmoid','tanh','relu']},
        'loss': {'values': ['cross_entropy']},
        'layers': {'values' : [4,5,6]},
        'neurons_per_layer' : {'values' : [32,64,128,256]},
        'learning_rate' : {'values' : [1e-1,1e-2,1e-3,1e-4]},
        'batch_size' : {'values' : [16,32,64]},
        'regularization' : {'values': [0,0.0005]},
        'beta' : {'values' : [0.5,0.9]},
        'beta1' : {'values' : [0.9]},
        'beta2' : {'values' : [0.999]},
        "Initialization" : {'values' :['random','Xavier']}
    }
}
sweep_id = wandb.sweep(sweep=sweep_config,project="Shubhodeep_Final_CS6190_DeepLearing_Assignment1")
wandb.agent(sweep_id, function=main,count=50) # calls main function for count number of times.
wandb.finish()