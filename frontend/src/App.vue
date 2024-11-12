<template>
  <div id="app">
    <router-link to="/">Home</router-link>

    <button @click="fetchDetailTypes">Detail Types</button>
    <button @click="fetchSchemes">Schemes</button>
    <button @click="checkAssembly">Check Assembly</button>

    <!-- Список типов деталей -->
    <div v-if="showDetailTypes && detailTypes.length">
      <h3>Detail Types</h3>
      <ul>
        <li v-for="type in detailTypes" :key="type.id">
          {{ type.name }}: {{ type.quantity }} ({{ type.type }})
          <button @click="deleteDetailType(type.id)">Delete</button>
          <button @click="openAddModal(type)">Add</button>
        </li>
      </ul>
    </div>

    <!-- Список схем -->
    <div v-if="showSchemes && schemes.length">
      <h3>Schemes</h3>
      <ul>
        <li v-for="scheme in schemes" :key="scheme.id">
          <button @click="fetchDetailsForScheme(scheme.id)">
            {{ scheme.scheme_name }}
          </button>
          <button @click="deleteScheme(scheme.id)">Delete</button>
        </li>
      </ul>
    </div>

    <!-- Детали выбранной схемы -->
    <div v-if="showDetailsForScheme && selectedSchemeDetails.length">
      <h3>Details for Selected Scheme</h3>
      <ul>
        <li v-for="detail in selectedSchemeDetails" :key="detail.id">
          {{ detail.name }}: {{ detail.quantity }} ({{ detail.type }})
        </li>
      </ul>
      <button @click="openAddDetailToSchemeModal">Add Detail to Scheme</button>
    </div>

     <!-- Модальное окно для изменения количества -->
     <div v-if="isAddModalOpen" class="modal">
      <div class="modal-content">
        <h3>Add Quantity to {{ selectedDetailType?.name }}</h3>
        <input type="number" v-model.number="additionalQuantity" placeholder="Enter quantity" />
        <button @click="addQuantity">Confirm</button>
        <button @click="closeAddModal">Cancel</button>
      </div>
    </div>

    <!-- Модальное окно для добавления новой детали к схеме -->
    <div v-if="isAddDetailToSchemeModalOpen" class="modal">
      <div class="modal-content">
        <h3>Select Detail and Quantity to Add to Scheme</h3>

        <form @submit.prevent="addDetailToScheme">
          <!-- Выпадающий список типов деталей -->
          <select v-model="selectedDetailTypeToAdd" required>
            <option v-for="type in detailTypes" :key="type.id" :value="type">
              {{ type.name }} ({{ type.description }})
            </option>
          </select>

          <!-- Поле для ввода количества -->
          <input type="number" v-model.number="newDetailQuantity" placeholder="Enter quantity" required />

          <button @click="addDetailToScheme">Add to Scheme</button>
          <button @click="closeAddDetailToSchemeModal">Cancel</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      detailTypes: [],
      schemes: [],
      selectedSchemeDetails: [],
      showDetailTypes: false,
      showSchemes: false,
      showDetailsForScheme: false,
      isAddModalOpen: false,
      isAddDetailToSchemeModalOpen: false,
      addQuantityValue: 0,
      selectedDetailTypeId: null,
      selectedDetailType: null,
      additionalQuantity: 0,
      selectedDetailTypeToAdd: null,
      newDetailQuantity: 0,
      selectedSchemeId: 1
    };
  },
  created() {
    // Загрузка доступных типов деталей с сервера
    this.fetchDetailTypes();
  },
  methods: {
    async fetchDetailTypes() {
      try {
        this.showDetailTypes = true;
        this.showSchemes = false;
        this.showDetailsForScheme = false;
        const response = await axios.get('http://localhost:8000/detail_types');
        this.detailTypes = response.data;
      } catch (error) {
        console.error('Error fetching detail types:', error);
      }
    },
    async fetchSchemes() {
      try {
        this.showSchemes = true;
        this.showDetailTypes = false;
        this.showDetailsForScheme = false;
        const response = await axios.get('http://localhost:8000/schemes');
        this.schemes = response.data;
        this.schemeDetails = response.data;
      } catch (error) {
        console.error('Error fetching schemes:', error);
      }
    },
    async fetchDetailsForScheme(schemeId) {
      try {
        this.showDetailsForScheme = true;
        this.showDetailTypes = false;
        this.showSchemes = false;
        this.selectedSchemeId = schemeId;
        const response = await axios.get(`http://localhost:8000/schemes/${schemeId}/details`);
        this.selectedSchemeDetails = response.data; // Присваиваем полученные данные
      } catch (error) {
        console.error('Error fetching details for scheme:', error);
      }
    },
    async deleteDetailType(id) {
      try {
        await axios.delete(`http://localhost:8000/detail_types/${id}`);
        this.fetchDetailTypes();
      } catch (error) {
        console.error('Error deleting detail type:', error);
      }
    },
    async deleteScheme(id) {
      try {
        await axios.delete(`http://localhost:8000/schemes/${id}`);
        this.fetchSchemes();
      } catch (error) {
        console.error('Error deleting scheme:', error);
      }
    },
    openAddModal(type) {
      this.selectedDetailType = type;
      this.isAddModalOpen = true;
    },
    closeAddModal() {
      this.isAddModalOpen = false;
      this.selectedDetailType = null;
      this.additionalQuantity = 0;
    },
    // Обработка добавления количества
    async addQuantity() {
      try {
        if (this.additionalQuantity > 0 && this.selectedDetailType) {
          // Отправка PUT запроса на сервер для изменения количества в БД
          const response = await axios.put(`http://localhost:8000/detail_types/${this.selectedDetailType.id}/add`, {
            quantity: this.additionalQuantity
          });

          if (response.status === 200) {
            // Обновление локального списка типов деталей после успешного запроса
            const updatedDetail = response.data; // Данные, которые вернутся с сервера
            const index = this.detailTypes.findIndex(item => item.id === updatedDetail.id);
            if (index !== -1) {
              this.detailTypes[index].quantity = updatedDetail.quantity; // Обновляем количество
            }

            // Закрытие модального окна
            this.closeAddModal();
          } else {
            console.error('Failed to update quantity');
          }
        }
      } catch (error) {
        console.error('Error adding quantity:', error);
      }
    },
    openAddDetailToSchemeModal() {
      this.isAddDetailToSchemeModalOpen = true;
      this.newDetailQuantity = 0;
      this.selectedDetailTypeToAdd = null;
    },
    // Метод для добавления детали в схему
    async addDetailToScheme() {
      try {
        if (this.newDetailQuantity > 0 && this.selectedDetailTypeToAdd) {
          // Отправляем POST запрос на добавление детали в схему
          const response = await axios.post(`http://localhost:8000/schemes/${this.selectedSchemeId}/add_detail`, {
            detail_type_id: this.selectedDetailTypeToAdd.id,
            quantity: this.newDetailQuantity
          });

          if (response.status === 200) {
            this.closeAddDetailToSchemeModal(); // Закрываем модальное окно после добавления

            // Обновляем список деталей схемы
            await this.fetchDetailsForScheme(this.selectedSchemeId);

          }
        }
      } catch (error) {
        console.error("Error adding detail to scheme:", error);
      }
    },
    closeAddDetailToSchemeModal() {
      this.isAddDetailToSchemeModalOpen = false;
      this.newDetailQuantity = 0; // Сбрасываем значение количества
      this.selectedDetailTypeToAdd = null; // Сбрасываем выбранный тип детали
    }
  }
};
</script>

<style>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
}
</style>
